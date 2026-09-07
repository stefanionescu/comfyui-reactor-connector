"""Serve local settings with request limits and no forwarding to Reactor."""

import asyncio
from aiohttp import web
from .guard import local_route
from ...config.routes import SETTINGS_PREFIX
from ..settings.store import ConfigurationStore
from collections.abc import Callable, Awaitable
from ..serialization import Json, parse_json, mapping_value
from ...config.settings import MAX_SETTINGS_BYTES, SETTINGS_TIMEOUT_SECONDS


async def read_document(request: web.Request, *, max_bytes: int = MAX_SETTINGS_BYTES) -> dict[str, Json]:
    """Read a size-limited JSON body, including without Content-Length."""
    if request.content_type != "application/json":
        raise web.HTTPUnsupportedMediaType(text="Send a JSON request.")
    if request.content_length is not None and request.content_length > max_bytes:
        raise web.HTTPRequestEntityTooLarge(max_size=max_bytes, actual_size=request.content_length)
    content = bytearray()
    try:
        async with asyncio.timeout(SETTINGS_TIMEOUT_SECONDS):
            async for chunk in request.content.iter_chunked(1024):
                content.extend(chunk)
                if len(content) > max_bytes:
                    raise web.HTTPRequestEntityTooLarge(max_size=max_bytes, actual_size=len(content))
    except TimeoutError:
        raise web.HTTPRequestTimeout(text="The configuration request took too long.") from None
    try:
        return mapping_value(parse_json(content.decode("utf-8"), max_bytes=max_bytes))
    except UnicodeError:
        raise web.HTTPBadRequest(text="Send valid UTF-8 JSON.") from None


class ConfigurationRoutes:
    """Register routes once during the host's extension load phase."""

    def __init__(self, store: ConfigurationStore, *, multi_user: bool = False) -> None:
        """Bind the configuration store and the host's multi-user access policy."""
        self.store = store
        self.multi_user = multi_user

    async def status(self, _request: web.Request) -> dict[str, Json]:
        """Return effective settings and whether the current host permits changes."""
        result = await asyncio.to_thread(self.store.status)
        result["mutation_allowed"] = not self.multi_user
        return result

    async def settings(self, request: web.Request) -> dict[str, Json]:
        """Validate a settings patch and save it against the caller's current revision."""
        document = await read_document(request)
        if document.keys() != {"revision", "settings"} or not isinstance(document["revision"], str):
            raise web.HTTPBadRequest(text="Send settings and their current revision.")
        return await asyncio.to_thread(
            self.store.update_settings, mapping_value(document["settings"]), document["revision"]
        )

    async def credential(self, request: web.Request) -> dict[str, Json]:
        """Accept one API key and save it only through the private configuration store."""
        document = await read_document(request)
        if document.keys() != {"api_key"} or not isinstance(document["api_key"], str):
            raise web.HTTPBadRequest(text="Send one API key.")
        return await asyncio.to_thread(self.store.set_credential, document["api_key"])

    async def clear_credential(self, request: web.Request) -> dict[str, Json]:
        """Remove the saved key after rejecting unexpected request content."""
        if request.can_read_body:
            raise web.HTTPBadRequest(text="Do not include a body when clearing a saved key.")
        return await asyncio.to_thread(self.store.clear_credential)

    def _guard(
        self, callback: Callable[[web.Request], Awaitable[dict[str, Json]]], *, mutation: bool
    ) -> Callable[[web.Request], Awaitable[web.Response]]:
        """Apply the host access policy to one configuration route."""
        return local_route(callback, mutation=mutation, multi_user=self.multi_user)

    def register(self, routes: web.RouteTableDef) -> None:
        """Register guarded status, settings, key-save, and key-removal endpoints."""
        routes.get(SETTINGS_PREFIX + "/status")(self._guard(self.status, mutation=False))
        routes.patch(SETTINGS_PREFIX + "/settings")(self._guard(self.settings, mutation=True))
        routes.put(SETTINGS_PREFIX + "/credential")(self._guard(self.credential, mutation=True))
        routes.delete(SETTINGS_PREFIX + "/credential")(self._guard(self.clear_credential, mutation=True))
