"""Let the local ComfyUI owner refresh public metadata without generation."""

import asyncio
from aiohttp import web
from .store import ModelStore
from .contracts import Snapshot
from ..language import translate
from ..serialization import Json
from .checker import ModelChecker
from ..http.guard import local_route
from .sources import read_public_models
from ..http.request import read_document
from ...config.routes import MODELS_PREFIX
from collections.abc import Callable, Awaitable


class ModelRoutes:
    """Local-owner endpoints for model metadata status, refresh, and rollback."""

    def __init__(
        self,
        store: ModelStore,
        *,
        multi_user: bool = False,
        fetcher: Callable[[], Awaitable[Snapshot]] = read_public_models,
        checker: ModelChecker | None = None,
    ) -> None:
        """Bind the model store, public fetcher, and optional scheduled checker."""
        self.store = store
        self.multi_user = multi_user
        self.fetcher = fetcher
        self.checker = checker

    def _add_route_fields(self, result: dict[str, Json]) -> dict[str, Json]:
        """Add catalog permissions and scheduled-check status to one response."""
        result["mutation_allowed"] = not self.multi_user
        if self.checker:
            result["automatic_check"] = self.checker.status(str(result["revision"]))
        return result

    async def status(self, _request: web.Request) -> dict[str, Json]:
        """Read the saved model list without blocking the host event loop."""
        return self._add_route_fields(await asyncio.to_thread(self.store.status))

    async def refresh(self, request: web.Request) -> dict[str, Json]:
        """Refresh public metadata and return the newly saved model list."""
        if request.can_read_body:
            raise web.HTTPBadRequest(text=translate("main", "errors.refreshBody"))
        result = await self.store.refresh(self.fetcher)
        return self._add_route_fields(result)

    async def rollback(self, request: web.Request) -> dict[str, Json]:
        """Restore the previous snapshot only if the caller still has the current revision."""
        body = await read_document(request)
        if body.keys() != {"revision"} or not isinstance(body["revision"], str):
            raise web.HTTPBadRequest(text=translate("main", "errors.modelRevisionRequired"))
        return self._add_route_fields(await asyncio.to_thread(self.store.rollback, body["revision"]))

    def register(self, routes: web.RouteTableDef) -> None:
        """Register model routes with local-owner and mutation guards."""
        for method, path, callback, mutation in (
            (routes.get, MODELS_PREFIX, self.status, False),
            (routes.post, MODELS_PREFIX + "/refresh", self.refresh, True),
            (routes.post, MODELS_PREFIX + "/rollback", self.rollback, True),
        ):
            method(path)(local_route(callback, mutation=mutation, multi_user=self.multi_user))
