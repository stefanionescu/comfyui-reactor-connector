"""Promote complete metadata snapshots atomically and retain one rollback copy."""

import json
import asyncio
import threading
from pathlib import Path
from ..codes import ErrorCode
from .views import model_views
from ..errors import ConnectorError
from .sources import read_public_models
from .contracts import invalid, Snapshot
from dataclasses import replace, dataclass
from collections.abc import Callable, Awaitable
from ..storage import atomic_write, read_private
from ..serialization import Json, parse_json, mapping_value

BUNDLED = Path(__file__).resolve().parents[2] / "config" / "bundled.json"


def read_snapshot(path: Path) -> Snapshot:
    """Read the packaged public snapshot; never fetch while importing or indexing nodes."""
    return Snapshot.parse(mapping_value(parse_json(path.read_text(), max_bytes=1_048_576)))


def merge_observations(previous: Snapshot, candidate: Snapshot) -> Snapshot:
    """Keep missing entries visible without claiming they remain available or current."""
    previous_ids = {price.id for price in previous.prices}
    new_ids = {price.id for price in candidate.prices}
    if len(new_ids - previous_ids) > max(20, len(previous_ids)):
        raise ConnectorError(ErrorCode.DISCOVERY, "The catalog grew unexpectedly. Review the source before updating.")
    if len(new_ids) < max(1, len([p for p in previous.prices if p.observed]) // 2):
        raise ConnectorError(ErrorCode.DISCOVERY, "The pricing list may be incomplete. The previous list is unchanged.")
    guide_slugs = {guide.slug for guide in candidate.guides}
    if len(guide_slugs) < max(1, len([g for g in previous.guides if g.observed]) // 2):
        raise ConnectorError(ErrorCode.DISCOVERY, "The guide list may be incomplete. The previous list is unchanged.")
    merged = replace(
        candidate,
        prices=candidate.prices
        + tuple(replace(price, observed=False) for price in previous.prices if price.id not in new_ids),
        guides=candidate.guides
        + tuple(replace(guide, observed=False) for guide in previous.guides if guide.slug not in guide_slugs),
    )
    return Snapshot.parse(merged.to_json())


@dataclass(frozen=True, slots=True)
class ModelState:
    """The current public snapshot and one optional rollback snapshot."""

    current: Snapshot
    previous: Snapshot | None = None

    def to_json(self) -> dict[str, Json]:
        """Serialize both snapshots in the versioned local storage format."""
        return {
            "version": 1,
            "current": self.current.to_json(),
            "previous": self.previous.to_json() if self.previous else None,
        }


class ModelStore:
    """Own local catalog reads, refresh admission, promotion, and rollback."""

    def __init__(self, directory: Path, *, bundled: Path = BUNDLED) -> None:
        """Select private storage and initialize separate state and refresh locks."""
        self.path = directory / "catalog.json"
        self.bundled = bundled
        self._lock = threading.Lock()
        self._admission_lock = threading.Lock()
        self._refreshing = False

    def _read(self) -> ModelState:
        """Load validated local state, or the bundled snapshot on first use."""
        try:
            payload = read_private(self.path, max_bytes=2_097_152)
        except FileNotFoundError:
            return ModelState(read_snapshot(self.bundled))
        value = mapping_value(parse_json(payload.decode(), max_bytes=2_097_152))
        if value.keys() != {"version", "current", "previous"} or type(value["version"]) is not int:
            raise invalid()
        if value["version"] != 1:
            raise invalid()
        return ModelState(
            Snapshot.parse(mapping_value(value["current"])),
            Snapshot.parse(mapping_value(value["previous"])) if value["previous"] is not None else None,
        )

    def status(self) -> dict[str, Json]:
        """Read a consistent model list while holding the state lock."""
        with self._lock:
            state = self._read()
            return self._view(state)

    def _view(self, state: ModelState) -> dict[str, Json]:
        """Describe model support, source freshness, and available list actions."""
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
        """Admit one metadata refresh and reject overlapping refresh requests."""
        with self._admission_lock:
            if self._refreshing:
                raise ConnectorError(ErrorCode.DISCOVERY, "A catalog refresh is already running.")
            self._refreshing = True

    def _revision(self) -> str:
        """Read the current revision while holding the state lock."""
        with self._lock:
            return self._read().current.revision

    def preview(self, candidate: Snapshot) -> tuple[str, str]:
        """Validate a candidate against the current snapshot without writing it."""
        with self._lock:
            current = self._read().current
            return current.revision, merge_observations(current, candidate).revision

    def _finish(self) -> None:
        """Release refresh admission after the fetch and any state write finish."""
        with self._admission_lock:
            self._refreshing = False

    def _is_refreshing(self) -> bool:
        """Read refresh admission while holding its lock."""
        with self._admission_lock:
            return self._refreshing

    def _promote(self, candidate: Snapshot, revision: str) -> dict[str, Json]:
        """Save a validated snapshot atomically and retain the prior distinct revision."""
        with self._lock:
            state = self._read()
            self._require_revision(state, revision)
            merged = merge_observations(state.current, candidate)
            previous = state.current if merged.revision != revision else state.previous
            updated = ModelState(merged, previous)
            atomic_write(self.path, (json.dumps(updated.to_json(), indent=2) + "\n").encode())
            return self._view(updated)

    async def refresh(self, fetcher: Callable[[], Awaitable[Snapshot]] = read_public_models) -> dict[str, Json]:
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
    def _require_revision(state: ModelState, revision: str) -> None:
        """Reject a write based on an outdated model-list revision."""
        if state.current.revision != revision:
            raise ConnectorError(ErrorCode.DISCOVERY, "The catalog changed. Reload the list and retry.")

    def rollback(self, revision: str) -> dict[str, Json]:
        """Swap current and prior snapshots atomically when no refresh is running."""
        with self._lock:
            if self._is_refreshing():
                raise ConnectorError(ErrorCode.DISCOVERY, "Wait for the catalog refresh to finish.")
            state = self._read()
            self._require_revision(state, revision)
            if state.previous is None:
                raise ConnectorError(ErrorCode.DISCOVERY, "There is no earlier catalog to restore.")
            restored = ModelState(state.previous, state.current)
            atomic_write(self.path, (json.dumps(restored.to_json(), indent=2) + "\n").encode())
            return self._view(restored)
