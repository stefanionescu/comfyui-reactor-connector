"""Share browser controls between threads and limit queued input."""

import secrets
import threading
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass

from ..errors import ConnectorError, ErrorCode
from ..json_data import Json


def unavailable() -> ConnectorError:
    return ConnectorError(ErrorCode.UNAVAILABLE, "This live session is no longer available.")


@dataclass(frozen=True, slots=True)
class BrowserInput:
    """Camera directions and their sequence number."""

    sequence: int
    axes: tuple[tuple[str, str], ...]
    end: bool
    received_at: float = 0.0
    release: bool = False


class BrowserLease:
    """Keep one controlling browser alive without sharing asyncio objects across loops."""

    def __init__(
        self, choices: dict[str, tuple[str, ...]], *, clock: Callable[[], float] = time.monotonic
    ) -> None:
        self.identifier = secrets.token_hex(16)
        self._capability = secrets.token_urlsafe(32)
        self.choices = choices.copy()
        self.clock = clock
        self.lock = threading.Lock()
        self.created_at = clock()
        self.last_seen = self.created_at
        self.sequence = -1
        self.axes = tuple((axis, "idle") for axis in choices)
        self.current_axes = self.axes
        self.pending: deque[BrowserInput] = deque()
        self.dropped_states = 0
        self.release_pending = False
        self.end = False
        self.end_requested = False
        self.ready = False
        self.controls_ready = False
        self.finishing = False
        self.closed = False
        self.termination_confirmed = False
        self.failed = False
        self.preview: str = ""
        self.preview_sequence = 0

    def __repr__(self) -> str:
        return "BrowserLease(<private>)"

    def invitation(self) -> dict[str, Json]:
        """Send only to the browser that owns the executing prompt."""
        return {
            "lease": self.identifier,
            "capability": self._capability,
            "axes": {axis: list(values) for axis, values in self.choices.items()},
        }

    def authorize(self, capability: Json) -> None:
        if (
            not isinstance(capability, str)
            or not capability.isascii()
            or len(capability) != 43
            or not secrets.compare_digest(capability, self._capability)
        ):
            raise unavailable()
        with self.lock:
            if self.closed or self.end or self.clock() - self.last_seen > 5:
                raise unavailable()

    def exchange(self, document: dict[str, Json]) -> dict[str, Json]:
        expected = {"lease", "capability", "sequence", "axes", "end", "release", "preview_sequence"}
        capability = document.get("capability")
        if (
            document.keys() != expected
            or not isinstance(capability, str)
            or not capability.isascii()
            or len(capability) != 43
            or not secrets.compare_digest(capability, self._capability)
        ):
            raise unavailable()
        sequence, axes, end = document["sequence"], document["axes"], document["end"]
        preview_sequence = document["preview_sequence"]
        release = document["release"]
        if (
            type(sequence) is not int
            or not 0 <= sequence < 2**53
            or type(preview_sequence) is not int
            or not 0 <= preview_sequence < 2**53
            or type(end) is not bool
            or type(release) is not bool
            or not isinstance(axes, dict)
            or axes.keys() != self.choices.keys()
            or any(value not in self.choices[axis] for axis, value in axes.items())
            or (release and any(value != "idle" for value in axes.values()))
        ):
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Send a complete listed camera state.")
        with self.lock:
            now = self.clock()
            if not self.closed and now - self.last_seen > 5:
                self.end = True
                raise unavailable()
            if sequence <= self.sequence:
                raise ConnectorError(ErrorCode.INVALID_INPUT, "The live input is out of order.")
            self.sequence = sequence
            self.last_seen = now
            if not self.closed:
                self.ready = True
                self.end_requested = self.end_requested or end
                self.end = self.end or end
                if not self.finishing:
                    self._accept_axes(sequence, axes, now, release=release)
            return {
                "closed": self.closed,
                "termination_confirmed": self.termination_confirmed,
                "failed": self.failed,
                "controls_ready": self.controls_ready and not self.closed,
                "finishing": self.finishing,
                "elapsed_seconds": round(now - self.created_at, 1),
                "preview_sequence": self.preview_sequence,
                "preview": self.preview if preview_sequence != self.preview_sequence else "",
            }

    def read(self) -> BrowserInput:
        with self.lock:
            age = self.clock() - self.last_seen
            stale_queue = self.pending and self.clock() - self.pending[0].received_at > 0.75
            if age > 0.75 or self.end or stale_queue:
                self.dropped_states += len(self.pending)
                self.pending.clear()
                self.axes = self.current_axes = tuple((axis, "idle") for axis in self.choices)
                self.release_pending = True
            if self.release_pending:
                self.release_pending = False
                return BrowserInput(
                    self.sequence,
                    self.current_axes,
                    self.end or self.closed or age > 5,
                    release=True,
                )
            if self.pending:
                state = self.pending.popleft()
                self.current_axes = state.axes
                return state
            return BrowserInput(
                self.sequence, self.current_axes, self.end or self.closed or age > 5
            )

    def _accept_axes(
        self, sequence: int, values: dict[str, Json], now: float, *, release: bool
    ) -> None:
        """Keep brief key presses; discard stale input to avoid delayed movement."""
        axes = tuple(
            (axis, value if isinstance(value, str) and not self.end else "idle")
            for axis in self.choices
            for value in (values[axis],)
        )
        state = BrowserInput(sequence, axes, self.end, now)
        if self.end or release:
            self.pending.clear()
            self.current_axes = axes
            self.release_pending = True
        elif axes != self.axes:
            if len(self.pending) >= 8:
                self.dropped_states += len(self.pending)
                self.pending.clear()
                self.current_axes = tuple((axis, "idle") for axis in self.choices)
                self.release_pending = True
            self.pending.append(state)
        elif self.pending and self.pending[-1].axes == axes:
            self.pending[-1] = state
        self.axes = axes

    def is_ready(self) -> bool:
        with self.lock:
            return self.ready and not self.end and not self.closed

    def was_ended_by_user(self) -> bool:
        with self.lock:
            return self.end_requested

    def enable_controls(self) -> None:
        with self.lock:
            if not self.closed:
                self.controls_ready = True

    def finish(self) -> None:
        with self.lock:
            self.finishing = True
            self.controls_ready = False
            self.pending.clear()

    def frame(self, encoded: str) -> None:
        if len(encoded) > 350_000:
            return
        with self.lock:
            if not self.closed:
                self.preview = encoded
                self.preview_sequence += 1

    def close(self, *, termination_confirmed: bool, failed: bool = False) -> None:
        with self.lock:
            self.closed = True
            self.end = True
            self.preview = ""
            self.pending.clear()
            self.termination_confirmed = termination_confirmed
            self.failed = failed


class BrowserRegistry:
    """Limit stored browser sessions and remove closed sessions after 30 seconds."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.leases: dict[str, BrowserLease] = {}

    def add(self, lease: BrowserLease) -> None:
        with self.lock:
            self.leases = {
                key: value
                for key, value in self.leases.items()
                if not value.closed or value.clock() - value.last_seen < 30
            }
            if len(self.leases) >= 32:
                raise ConnectorError(ErrorCode.UNAVAILABLE, "Too many live panels are still open.")
            self.leases[lease.identifier] = lease

    def exchange(self, document: dict[str, Json]) -> dict[str, Json]:
        identifier = document.get("lease")
        with self.lock:
            lease = self.leases.get(identifier) if isinstance(identifier, str) else None
        if lease is None:
            raise unavailable()
        return lease.exchange(document)
