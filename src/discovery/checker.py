"""Check public metadata on a schedule without promoting it or opening sessions."""

import time
import asyncio
from aiohttp import web
from .store import ModelStore
from .contracts import Snapshot
from ..language import translate
from ..serialization import Json
from datetime import UTC, datetime
from .sources import read_public_models
from ..settings.settings import Settings
from ...config.settings import INTEGER_SETTINGS
from collections.abc import Callable, Awaitable, AsyncIterator
from ...config.discovery import CHECK_POLL_SECONDS, CHECK_TIMEOUT_SECONDS


class ModelChecker:
    """Check for model updates with a request timeout and keep the last valid result."""

    def __init__(
        self,
        store: ModelStore,
        settings: Callable[[], Settings],
        *,
        fetcher: Callable[[], Awaitable[Snapshot]] = read_public_models,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """Store metadata sources and initialize the update schedule without fetching."""
        self.store = store
        self.settings = settings
        self.fetcher = fetcher
        self.clock = clock
        self.last_attempt: float | None = None
        self.checked_at: str | None = None
        self.base_revision: str | None = None
        self.candidate_revision: str | None = None
        self.error_key: str | None = None
        self.running = False
        self.enabled = False
        self.interval_hours = INTEGER_SETTINGS["catalog_interval_hours"]["default"]

    def status(self, revision: str) -> dict[str, Json]:
        """Describe the last check relative to the model revision shown by the caller."""
        return {
            "enabled": self.enabled,
            "interval_hours": self.interval_hours,
            "running": self.running,
            "checked_at": self.checked_at,
            "update_available": self.candidate_revision != revision
            if self.base_revision == revision and self.candidate_revision is not None
            else None,
            "error": translate("main", self.error_key) if self.error_key else None,
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
            if self.last_attempt is not None and now - self.last_attempt < self.interval_hours * 3600:
                return
            self.last_attempt = now
            self.running = True
            async with asyncio.timeout(CHECK_TIMEOUT_SECONDS):
                candidate = await self.fetcher()
                base, merged = await asyncio.to_thread(self.store.preview, candidate)
            self.base_revision, self.candidate_revision = base, merged
            self.checked_at = datetime.now(UTC).isoformat()
            self.error_key = None
        except Exception:  # noqa: BLE001 -- reason: Keep background failures recoverable without exposing provider URLs or response bodies.
            # Provider exceptions can contain URLs or response bodies. The settings
            # and model dialogs need a recovery action, not those private details.
            self.error_key = "errors.automaticCheckFailed"
        finally:
            self.running = False

    async def run(self) -> None:
        """Poll settings and check for updates only when the configured interval expires."""
        while True:
            await self.tick()
            await asyncio.sleep(CHECK_POLL_SECONDS)

    async def lifecycle(self, _app: web.Application) -> AsyncIterator[None]:
        """Start with aiohttp and await cancellation before the host shuts down."""
        task = asyncio.create_task(self.run(), name="reactor-catalog-check")
        try:
            yield
        finally:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
