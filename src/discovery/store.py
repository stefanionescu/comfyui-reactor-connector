"""Promote complete metadata snapshots atomically and retain one rollback copy."""

import json
import asyncio
import threading
from pathlib import Path
from .views import model_views
from dataclasses import replace
from ..language import translate
from ..state.documents import Json
from .sources import read_public_models
from ..errors import ErrorCode, ConnectorError
from .contracts import invalid, parse_snapshot
from collections.abc import Callable, Awaitable
from ..storage import atomic_write, read_private
from ..serialization import parse_json, mapping_value
from ..state.discovery import Snapshot, CatalogState, STORAGE_VERSION
from ...config.discovery import MAX_ADDED_MODELS, SOURCE_RETENTION_DIVISOR, MAX_STORED_METADATA_BYTES


class ModelStore:
    """Own local catalog reads, refresh admission, promotion, and rollback."""

    def __init__(self, directory: Path, node_models: dict[str, str]) -> None:
        """Select private storage and initialize separate state and refresh locks."""
        self._storage_path = directory / "catalog.json"
        self._node_models = node_models.copy()
        self._lock = threading.Lock()
        self._admission_lock = threading.Lock()
        self._refreshing = False

    def _read(self) -> CatalogState:
        """Load cached public metadata, or start without prices before the first refresh."""
        try:
            payload = read_private(self._storage_path, max_bytes=MAX_STORED_METADATA_BYTES)
        except FileNotFoundError:
            return CatalogState()
        value = mapping_value(parse_json(payload.decode(), max_bytes=MAX_STORED_METADATA_BYTES))
        if value.keys() != {"version", "current", "previous"} or type(value["version"]) is not int:
            raise invalid()
        if value["version"] != STORAGE_VERSION:
            raise invalid()
        return CatalogState(
            parse_snapshot(mapping_value(value["current"])),
            parse_snapshot(mapping_value(value["previous"])) if value["previous"] is not None else None,
        )

    def status(self) -> dict[str, Json]:
        """Read a consistent model list while holding the state lock."""
        with self._lock:
            state = self._read()
            return self._build_status(state)

    def _build_status(self, state: CatalogState) -> dict[str, Json]:
        """Describe model support, source freshness, and available list actions."""
        models: list[Json] = list(model_views(state.current, self._node_models))
        return {
            "revision": state.revision,
            "retrieved_at": state.current.retrieved_at if state.current else None,
            "models": models,
            "can_rollback": state.previous is not None,
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
            return state.revision, _merge_observations(state.current, candidate).revision

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
            merged = _merge_observations(state.current, candidate)
            previous = state.current if merged.revision != revision else state.previous
            updated = CatalogState(merged, previous)
            atomic_write(self._storage_path, (json.dumps(updated.to_json(), indent=2) + "\n").encode())
            return self._build_status(updated)

    async def refresh(self, fetcher: Callable[[], Awaitable[Snapshot]] = read_public_models) -> dict[str, Json]:
        """Fetch without holding the state lock and reject overlapping refreshes."""
        self._begin()
        try:
            revision = await asyncio.to_thread(self._revision)
            candidate = await fetcher()
            return await self._promote_owned(candidate, revision)
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
            restored = CatalogState(state.previous, state.current)
            atomic_write(self._storage_path, (json.dumps(restored.to_json(), indent=2) + "\n").encode())
            return self._build_status(restored)


def _merge_observations(previous: Snapshot | None, candidate: Snapshot) -> Snapshot:
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
    return parse_snapshot(merged.to_json())
