"""Promote complete metadata snapshots atomically and retain one rollback copy."""

import asyncio
import json
import threading
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, replace
from pathlib import Path

from ..errors import ConnectorError, ErrorCode
from ..json_data import Json, object_value, parse_json
from ..storage import atomic_write, read_private
from .contracts import Snapshot, invalid
from .sources import fetch_public_catalog
from .views import model_views

BUNDLED = Path(__file__).with_name("bundled.json")


def read_snapshot(path: Path) -> Snapshot:
    """Read the packaged public snapshot; never fetch while importing or indexing nodes."""
    return Snapshot.parse(object_value(parse_json(path.read_text(), max_bytes=1_048_576)))


def merge_observations(previous: Snapshot, candidate: Snapshot) -> Snapshot:
    """Keep missing entries visible without claiming they remain available or current."""
    old_ids = {price.id for price in previous.prices}
    new_ids = {price.id for price in candidate.prices}
    if len(new_ids - old_ids) > max(20, len(old_ids)):
        raise ConnectorError(
            ErrorCode.CATALOG, "The catalog grew unexpectedly. Review the source before updating."
        )
    if len(new_ids) < max(1, len([p for p in previous.prices if p.observed]) // 2):
        raise ConnectorError(
            ErrorCode.CATALOG, "The pricing list may be incomplete. The previous list is unchanged."
        )
    guide_slugs = {guide.slug for guide in candidate.guides}
    if len(guide_slugs) < max(1, len([g for g in previous.guides if g.observed]) // 2):
        raise ConnectorError(
            ErrorCode.CATALOG, "The guide list may be incomplete. The previous list is unchanged."
        )
    merged = replace(
        candidate,
        prices=candidate.prices
        + tuple(
            replace(price, observed=False) for price in previous.prices if price.id not in new_ids
        ),
        guides=candidate.guides
        + tuple(
            replace(guide, observed=False)
            for guide in previous.guides
            if guide.slug not in guide_slugs
        ),
    )
    return Snapshot.parse(merged.to_json())


@dataclass(frozen=True, slots=True)
class CatalogState:
    current: Snapshot
    previous: Snapshot | None = None

    def to_json(self) -> dict[str, Json]:
        return {
            "version": 1,
            "current": self.current.to_json(),
            "previous": self.previous.to_json() if self.previous else None,
        }


class CatalogStore:
    """Own local catalog reads, refresh admission, promotion, and rollback."""

    def __init__(self, directory: Path, *, bundled: Path = BUNDLED) -> None:
        self.path = directory / "catalog.json"
        self.bundled = bundled
        self._lock = threading.Lock()
        self._admission_lock = threading.Lock()
        self._refreshing = False

    def _load(self) -> CatalogState:
        try:
            data = read_private(self.path, max_bytes=2_097_152)
        except FileNotFoundError:
            return CatalogState(read_snapshot(self.bundled))
        value = object_value(parse_json(data.decode(), max_bytes=2_097_152))
        if value.keys() != {"version", "current", "previous"} or type(value["version"]) is not int:
            raise invalid()
        if value["version"] != 1:
            raise invalid()
        return CatalogState(
            Snapshot.parse(object_value(value["current"])),
            Snapshot.parse(object_value(value["previous"]))
            if value["previous"] is not None
            else None,
        )

    def status(self) -> dict[str, Json]:
        with self._lock:
            state = self._load()
            return self._view(state)

    def _view(self, state: CatalogState) -> dict[str, Json]:
        models: list[Json] = list(model_views(state.current))
        return {
            "revision": state.current.revision,
            "retrieved_at": state.current.retrieved_at,
            "credits_per_dollar": state.current.credits_per_dollar,
            "models": models,
            "can_rollback": state.previous is not None,
            "refreshing": self._is_refreshing(),
            "source": "local" if self.path.exists() else "bundled",
            "scope": "public_pricing_and_documentation",
        }

    def _begin(self) -> None:
        with self._admission_lock:
            if self._refreshing:
                raise ConnectorError(ErrorCode.CATALOG, "A catalog refresh is already running.")
            self._refreshing = True

    def _revision(self) -> str:
        with self._lock:
            return self._load().current.revision

    def preview(self, candidate: Snapshot) -> tuple[str, str]:
        """Validate a candidate against the current snapshot without writing it."""
        with self._lock:
            current = self._load().current
            return current.revision, merge_observations(current, candidate).revision

    def _finish(self) -> None:
        with self._admission_lock:
            self._refreshing = False

    def _is_refreshing(self) -> bool:
        with self._admission_lock:
            return self._refreshing

    def _promote(self, candidate: Snapshot, revision: str) -> dict[str, Json]:
        with self._lock:
            state = self._load()
            self._require_revision(state, revision)
            merged = merge_observations(state.current, candidate)
            previous = state.current if merged.revision != revision else state.previous
            updated = CatalogState(merged, previous)
            atomic_write(self.path, (json.dumps(updated.to_json(), indent=2) + "\n").encode())
            return self._view(updated)

    async def refresh(
        self, fetcher: Callable[[], Awaitable[Snapshot]] = fetch_public_catalog
    ) -> dict[str, Json]:
        """Fetch without holding the state lock and reject overlapping refreshes."""
        self._begin()
        try:
            revision = await asyncio.to_thread(self._revision)
            candidate = await fetcher()
            result = await self._promote_owned(candidate, revision)
            result["refreshing"] = False
            return result
        finally:
            self._finish()

    async def _promote_owned(self, candidate: Snapshot, revision: str) -> dict[str, Json]:
        """Keep refresh admission until an atomic write has finished, even after cancellation."""
        task = asyncio.create_task(asyncio.to_thread(self._promote, candidate, revision))
        cancelled = False
        while not task.done():
            try:
                await asyncio.shield(task)
            except asyncio.CancelledError:
                cancelled = True
        if cancelled:
            task.exception()
            raise asyncio.CancelledError
        return task.result()

    @staticmethod
    def _require_revision(state: CatalogState, revision: str) -> None:
        if state.current.revision != revision:
            raise ConnectorError(
                ErrorCode.CATALOG, "The catalog changed. Reload the list and retry."
            )

    def rollback(self, revision: str) -> dict[str, Json]:
        with self._lock:
            if self._is_refreshing():
                raise ConnectorError(ErrorCode.CATALOG, "Wait for the catalog refresh to finish.")
            state = self._load()
            self._require_revision(state, revision)
            if state.previous is None:
                raise ConnectorError(ErrorCode.CATALOG, "There is no earlier catalog to restore.")
            restored = CatalogState(state.previous, state.current)
            atomic_write(self.path, (json.dumps(restored.to_json(), indent=2) + "\n").encode())
            return self._view(restored)
