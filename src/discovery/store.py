"""Promote complete metadata snapshots atomically and retain one rollback copy."""

import json
import asyncio
import threading
from pathlib import Path
from .state import ModelState
from .views import model_views
from dataclasses import replace
from ..language import translate
from .sources import read_public_models
from .contracts import invalid, Snapshot
from ..errors import ErrorCode, ConnectorError
from collections.abc import Callable, Awaitable
from ..storage import atomic_write, read_private
from ..serialization import Json, parse_json, mapping_value
from ...config.discovery import MAX_ADDED_MODELS, SOURCE_RETENTION_DIVISOR, MAX_STORED_METADATA_BYTES


class ModelStore:
    """Own local catalog reads, refresh admission, promotion, and rollback."""

    def __init__(self, directory: Path) -> None:
        """Select private storage and initialize separate state and refresh locks."""
        self.path = directory / "catalog.json"
        self._lock = threading.Lock()
        self._admission_lock = threading.Lock()
        self._refreshing = False

    def _read(self) -> ModelState:
        """Load cached public metadata, or start without prices before the first refresh."""
        try:
            payload = read_private(self.path, max_bytes=MAX_STORED_METADATA_BYTES)
        except FileNotFoundError:
            return ModelState()
        value = mapping_value(parse_json(payload.decode(), max_bytes=MAX_STORED_METADATA_BYTES))
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
            "revision": state.revision,
            "retrieved_at": state.current.retrieved_at if state.current else None,
            "credits_per_dollar": state.current.credits_per_dollar if state.current else None,
            "models": models,
            "can_rollback": state.previous is not None,
            "refreshing": self._is_refreshing(),
            "source": "local" if state.current else "registered",
            "scope": "public_pricing_and_documentation",
        }

    def _begin(self) -> None:
        """Admit one metadata refresh and reject overlapping refresh requests."""
        with self._admission_lock:
            if self._refreshing:
                raise ConnectorError(ErrorCode.DISCOVERY, translate("main", "errors.modelRefreshRunning"))
            self._refreshing = True

    def _revision(self) -> str:
        """Read the current revision while holding the state lock."""
        with self._lock:
            return self._read().revision

    def preview(self, candidate: Snapshot) -> tuple[str, str]:
        """Validate a candidate against the current snapshot without writing it."""
        with self._lock:
            state = self._read()
            return state.revision, merge_observations(state.current, candidate).revision

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
        if state.revision != revision:
            raise ConnectorError(ErrorCode.DISCOVERY, translate("main", "errors.modelListChanged"))

    def rollback(self, revision: str) -> dict[str, Json]:
        """Swap current and prior snapshots atomically when no refresh is running."""
        with self._lock:
            if self._is_refreshing():
                raise ConnectorError(ErrorCode.DISCOVERY, translate("main", "errors.modelRefreshWait"))
            state = self._read()
            self._require_revision(state, revision)
            if state.previous is None:
                raise ConnectorError(ErrorCode.DISCOVERY, translate("main", "errors.modelListHistoryEmpty"))
            restored = ModelState(state.previous, state.current)
            atomic_write(self.path, (json.dumps(restored.to_json(), indent=2) + "\n").encode())
            return self._view(restored)


def merge_observations(previous: Snapshot | None, candidate: Snapshot) -> Snapshot:
    """Keep missing entries visible without claiming they remain available or current."""
    if previous is None:
        return candidate
    previous_ids = {price.id for price in previous.prices}
    new_ids = {price.id for price in candidate.prices}
    if len(new_ids - previous_ids) > max(MAX_ADDED_MODELS, len(previous_ids)):
        raise ConnectorError(ErrorCode.DISCOVERY, translate("main", "errors.modelListGrowth"))
    if len(new_ids) < max(1, len([p for p in previous.prices if p.observed]) // SOURCE_RETENTION_DIVISOR):
        raise ConnectorError(ErrorCode.DISCOVERY, translate("main", "errors.priceListIncomplete"))
    guide_slugs = {guide.slug for guide in candidate.guides}
    if len(guide_slugs) < max(1, len([g for g in previous.guides if g.observed]) // SOURCE_RETENTION_DIVISOR):
        raise ConnectorError(ErrorCode.DISCOVERY, translate("main", "errors.guideListIncomplete"))
    merged = replace(
        candidate,
        prices=candidate.prices
        + tuple(replace(price, observed=False) for price in previous.prices if price.id not in new_ids),
        guides=candidate.guides
        + tuple(replace(guide, observed=False) for guide in previous.guides if guide.slug not in guide_slugs),
    )
    return Snapshot.parse(merged.to_json())
