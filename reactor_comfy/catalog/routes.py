"""Let the local ComfyUI owner refresh public metadata without generation."""

import asyncio
from collections.abc import Awaitable, Callable

from aiohttp import web

from ..http_guard import local_route
from ..http_routes import read_document
from ..json_data import Json
from .checker import CatalogChecker
from .contracts import Snapshot
from .sources import fetch_public_catalog
from .store import CatalogStore

PREFIX = "/reactor-inc/v1/catalog"


class CatalogRoutes:
    def __init__(
        self,
        store: CatalogStore,
        *,
        multi_user: bool = False,
        fetcher: Callable[[], Awaitable[Snapshot]] = fetch_public_catalog,
        checker: CatalogChecker | None = None,
    ) -> None:
        self.store = store
        self.multi_user = multi_user
        self.fetcher = fetcher
        self.checker = checker

    def _with_check(self, result: dict[str, Json]) -> dict[str, Json]:
        if self.checker:
            result["automatic_check"] = self.checker.status(str(result["revision"]))
        return result

    async def status(self, request: web.Request) -> dict[str, Json]:
        return self._with_check(await asyncio.to_thread(self.store.status))

    async def refresh(self, request: web.Request) -> dict[str, Json]:
        if request.can_read_body:
            raise web.HTTPBadRequest(text="Do not send a body when refreshing public models.")
        result = await self.store.refresh(self.fetcher)
        result["refreshing"] = False
        return self._with_check(result)

    async def rollback(self, request: web.Request) -> dict[str, Json]:
        body = await read_document(request)
        if body.keys() != {"revision"} or not isinstance(body["revision"], str):
            raise web.HTTPBadRequest(text="Send the catalog revision shown in this tab.")
        return self._with_check(await asyncio.to_thread(self.store.rollback, body["revision"]))

    def register(self, routes: web.RouteTableDef) -> None:
        for method, path, handler, mutation in (
            (routes.get, PREFIX, self.status, False),
            (routes.post, PREFIX + "/refresh", self.refresh, True),
            (routes.post, PREFIX + "/rollback", self.rollback, True),
        ):
            method(path)(local_route(handler, mutation=mutation, multi_user=self.multi_user))
