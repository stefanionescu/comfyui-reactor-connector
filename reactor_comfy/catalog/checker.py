"""Check public metadata on a schedule without promoting it or opening sessions."""

import asyncio
import time
from collections.abc import AsyncIterator, Awaitable, Callable
from datetime import UTC, datetime

from aiohttp import web

from ..config import Settings
from ..json_data import Json
from .contracts import Snapshot
from .sources import fetch_public_catalog
from .store import CatalogStore


class CatalogChecker:
    """Check for model updates with a request timeout and keep the last valid result."""

    def __init__(
        self,
        store: CatalogStore,
        settings: Callable[[], Settings],
        *,
        fetcher: Callable[[], Awaitable[Snapshot]] = fetch_public_catalog,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.store = store
        self.settings = settings
        self.fetcher = fetcher
        self.clock = clock
        self.last_attempt: float | None = None
        self.checked_at: str | None = None
        self.base_revision: str | None = None
        self.candidate_revision: str | None = None
        self.error: str | None = None
        self.running = False
        self.enabled = False
        self.interval_hours = 24

    def status(self, revision: str) -> dict[str, Json]:
        return {
            "enabled": self.enabled,
            "interval_hours": self.interval_hours,
            "running": self.running,
            "checked_at": self.checked_at,
            "update_available": self.candidate_revision != revision
            if self.base_revision == revision and self.candidate_revision is not None
            else None,
            "error": self.error,
        }

    async def tick(self) -> None:
        """Honor current settings and retry failures only after the configured interval."""
        if self.running:
            return
        try:
            settings = await asyncio.to_thread(self.settings)
            self.enabled = settings.catalog_auto_check
            self.interval_hours = settings.catalog_interval_hours
            if not self.enabled:
                return
            now = self.clock()
            if (
                self.last_attempt is not None
                and now - self.last_attempt < self.interval_hours * 3600
            ):
                return
            self.last_attempt = now
            self.running = True
            async with asyncio.timeout(25):
                candidate = await self.fetcher()
                base, merged = await asyncio.to_thread(self.store.preview, candidate)
            self.base_revision, self.candidate_revision = base, merged
            self.checked_at = datetime.now(UTC).isoformat()
            self.error = None
        except Exception:
            # Provider exceptions can contain URLs or response bodies. The settings
            # and model dialogs need a recovery action, not those private details.
            self.error = "Automatic model check failed. Use Refresh models to retry."
        finally:
            self.running = False

    async def run(self) -> None:
        while True:
            await self.tick()
            await asyncio.sleep(60)

    async def lifecycle(self, app: web.Application) -> AsyncIterator[None]:
        """Start with aiohttp and await cancellation before the host shuts down."""
        task = asyncio.create_task(self.run(), name="reactor-catalog-check")
        try:
            yield
        finally:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
