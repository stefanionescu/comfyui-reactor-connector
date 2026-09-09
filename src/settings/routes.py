"""Serve private settings and credential changes through guarded local routes."""

import asyncio
from aiohttp import web
from ..language import translate
from ..http.guard import local_route
from .store import ConfigurationStore
from ..http.request import read_document
from ...config.routes import SETTINGS_PREFIX
from ..serialization import Json, mapping_value
from collections.abc import Callable, Awaitable


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
            raise web.HTTPBadRequest(text=translate("main", "errors.settingsRevisionRequired"))
        return await asyncio.to_thread(
            self.store.update_settings, mapping_value(document["settings"]), document["revision"]
        )

    async def credential(self, request: web.Request) -> dict[str, Json]:
        """Accept one API key and save it only through the private configuration store."""
        document = await read_document(request)
        if document.keys() != {"api_key"} or not isinstance(document["api_key"], str):
            raise web.HTTPBadRequest(text=translate("main", "errors.singleKeyRequired"))
        return await asyncio.to_thread(self.store.save_credential, document["api_key"])

    async def clear_credential(self, request: web.Request) -> dict[str, Json]:
        """Remove the saved key after rejecting unexpected request content."""
        if request.can_read_body:
            raise web.HTTPBadRequest(text=translate("main", "errors.clearKeyBody"))
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
