"""Provide local settings routes with request limits; do not forward provider calls."""

import asyncio
from collections.abc import Awaitable, Callable

from aiohttp import web

from .config_store import ConfigurationStore
from .http_guard import local_route
from .json_data import Json, object_value, parse_json

PREFIX = "/reactor-inc/v1"


async def read_document(request: web.Request, *, max_bytes: int = 4096) -> dict[str, Json]:
    """Read a size-limited JSON body, including without Content-Length."""
    if request.content_type != "application/json":
        raise web.HTTPUnsupportedMediaType(text="Send a JSON request.")
    if request.content_length is not None and request.content_length > max_bytes:
        raise web.HTTPRequestEntityTooLarge(max_size=max_bytes, actual_size=request.content_length)
    data = bytearray()
    try:
        async with asyncio.timeout(5):
            async for chunk in request.content.iter_chunked(1024):
                data.extend(chunk)
                if len(data) > max_bytes:
                    raise web.HTTPRequestEntityTooLarge(max_size=max_bytes, actual_size=len(data))
    except TimeoutError:
        raise web.HTTPRequestTimeout(text="The configuration request took too long.") from None
    try:
        return object_value(parse_json(data.decode("utf-8"), max_bytes=max_bytes))
    except UnicodeError:
        raise web.HTTPBadRequest(text="Send valid UTF-8 JSON.") from None


class ConfigurationRoutes:
    """Register routes once during the host's extension load phase."""

    def __init__(self, store: ConfigurationStore, *, multi_user: bool = False) -> None:
        self.store = store
        self.multi_user = multi_user

    async def status(self, request: web.Request) -> dict[str, Json]:
        result = await asyncio.to_thread(self.store.status)
        result["mutation_allowed"] = not self.multi_user
        return result

    async def settings(self, request: web.Request) -> dict[str, Json]:
        document = await read_document(request)
        if document.keys() != {"revision", "settings"} or not isinstance(document["revision"], str):
            raise web.HTTPBadRequest(text="Send settings and their current revision.")
        return await asyncio.to_thread(
            self.store.update_settings, object_value(document["settings"]), document["revision"]
        )

    async def credential(self, request: web.Request) -> dict[str, Json]:
        document = await read_document(request)
        if document.keys() != {"api_key"} or not isinstance(document["api_key"], str):
            raise web.HTTPBadRequest(text="Send one API key.")
        return await asyncio.to_thread(self.store.set_credential, document["api_key"])

    async def clear_credential(self, request: web.Request) -> dict[str, Json]:
        if request.can_read_body:
            raise web.HTTPBadRequest(text="Do not include a body when clearing a saved key.")
        return await asyncio.to_thread(self.store.clear_credential)

    def _guard(
        self, handler: Callable[[web.Request], Awaitable[dict[str, Json]]], *, mutation: bool
    ) -> Callable[[web.Request], Awaitable[web.Response]]:
        return local_route(handler, mutation=mutation, multi_user=self.multi_user)

    def register(self, routes: web.RouteTableDef) -> None:
        routes.get(PREFIX + "/status")(self._guard(self.status, mutation=False))
        routes.patch(PREFIX + "/settings")(self._guard(self.settings, mutation=True))
        routes.put(PREFIX + "/credential")(self._guard(self.credential, mutation=True))
        routes.delete(PREFIX + "/credential")(self._guard(self.clear_credential, mutation=True))
