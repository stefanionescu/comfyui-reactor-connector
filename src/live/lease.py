"""Share browser controls between threads and limit queued input."""

import time
import secrets
import threading
from collections import deque
from ..language import translate
from ..state.documents import Json
from collections.abc import Callable
from ..errors import ErrorCode, ConnectorError
from ..state.live import BrowserInput, BrowserExchange
from ...config.live import (
    LEASE_BYTES,
    MAX_SEQUENCE,
    CAPABILITY_BYTES,
    MAX_PENDING_INPUTS,
    STALE_INPUT_SECONDS,
    CAPABILITY_CHARACTERS,
    CLIENT_TIMEOUT_SECONDS,
    MAX_PREVIEW_CHARACTERS,
)


class BrowserLease:
    """Keep one controlling browser alive without sharing asyncio objects across loops."""

    def __init__(self, choices: dict[str, tuple[str, ...]], *, clock: Callable[[], float] = time.monotonic) -> None:
        """Create a private client capability and thread-safe input and preview state."""
        self.identifier = secrets.token_hex(LEASE_BYTES)
        self._capability = secrets.token_urlsafe(CAPABILITY_BYTES)
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
        self.is_termination_confirmed = False
        self.failed = False
        self.preview: str = ""
        self.preview_sequence = 0

    def __repr__(self) -> str:
        """Hide session identifiers and capabilities from object representations."""
        return "BrowserLease(<private>)"

    def invitation(self) -> dict[str, Json]:
        """Send only to the browser that owns the executing prompt."""
        return {
            "lease": self.identifier,
            "capability": self._capability,
            "axes": {axis: list(values) for axis, values in self.choices.items()},
        }

    def authorize(self, capability: Json) -> None:
        """Require the exact private capability and a live, recently connected client."""
        self._validate_capability(capability)
        with self.lock:
            if self.closed or self.end or self.clock() - self.last_seen > CLIENT_TIMEOUT_SECONDS:
                raise unavailable()

    def _validate_capability(self, capability: Json) -> None:
        """Compare a size-limited capability without exposing session state."""
        if (
            not isinstance(capability, str)
            or not capability.isascii()
            or len(capability) != CAPABILITY_CHARACTERS
            or not secrets.compare_digest(capability, self._capability)
        ):
            raise unavailable()

    def _parse_exchange(self, document: dict[str, Json]) -> BrowserExchange:
        """Validate untrusted browser state before acquiring the session lock."""
        expected = {"lease", "capability", "sequence", "axes", "end", "release", "preview_sequence"}
        if document.keys() != expected:
            raise unavailable()
        self._validate_capability(document["capability"])
        sequence, axes, end = document["sequence"], document["axes"], document["end"]
        preview_sequence = document["preview_sequence"]
        release = document["release"]
        if (
            type(sequence) is not int
            or not 0 <= sequence <= MAX_SEQUENCE
            or type(preview_sequence) is not int
            or not 0 <= preview_sequence <= MAX_SEQUENCE
            or type(end) is not bool
            or type(release) is not bool
            or not isinstance(axes, dict)
            or axes.keys() != self.choices.keys()
            or any(value not in self.choices[axis] for axis, value in axes.items())
            or (release and any(value != "idle" for value in axes.values()))
        ):
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.cameraStateRequired"))
        return BrowserExchange(sequence, axes, end, release, preview_sequence)

    def _accept_exchange(self, exchange: BrowserExchange, now: float) -> None:
        """Apply ordered browser state while the caller holds the session lock."""
        if not self.closed and now - self.last_seen > CLIENT_TIMEOUT_SECONDS:
            self.end = True
            raise unavailable()
        if exchange.sequence <= self.sequence:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.liveInputOrder"))
        self.sequence = exchange.sequence
        self.last_seen = now
        if not self.closed:
            self.ready = True
            self.end_requested = self.end_requested or exchange.end
            self.end = self.end or exchange.end
            if not self.finishing:
                self._accept_axes(exchange.sequence, exchange.axes, now, release=exchange.release)

    def _status(self, now: float, preview_sequence: int) -> dict[str, Json]:
        """Serialize session status while the caller holds the session lock."""
        return {
            "closed": self.closed,
            "termination_confirmed": self.is_termination_confirmed,
            "failed": self.failed,
            "controls_ready": self.controls_ready and not self.closed,
            "finishing": self.finishing,
            "elapsed_seconds": round(now - self.created_at, 1),
            "preview_sequence": self.preview_sequence,
            "preview": self.preview if preview_sequence != self.preview_sequence else "",
        }

    def exchange(self, document: dict[str, Json]) -> dict[str, Json]:
        """Validate client state, accept ordered input, and return the latest session status."""
        exchange = self._parse_exchange(document)
        with self.lock:
            now = self.clock()
            self._accept_exchange(exchange, now)
            return self._status(now, exchange.preview_sequence)

    def read(self) -> BrowserInput:
        """Read queued movement or release controls when input becomes stale."""
        with self.lock:
            age = self.clock() - self.last_seen
            stale_queue = self.pending and self.clock() - self.pending[0].received_at > STALE_INPUT_SECONDS
            if age > STALE_INPUT_SECONDS or self.end or stale_queue:
                self.dropped_states += len(self.pending)
                self.pending.clear()
                self.axes = self.current_axes = tuple((axis, "idle") for axis in self.choices)
                self.release_pending = True
            if self.release_pending:
                self.release_pending = False
                return BrowserInput(
                    self.sequence,
                    self.current_axes,
                    self.end or self.closed or age > CLIENT_TIMEOUT_SECONDS,
                    release=True,
                )
            if self.pending:
                state = self.pending.popleft()
                self.current_axes = state.axes
                return state
            return BrowserInput(
                self.sequence, self.current_axes, self.end or self.closed or age > CLIENT_TIMEOUT_SECONDS
            )

    def _accept_axes(self, sequence: int, values: dict[str, Json], now: float, *, release: bool) -> None:
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
            if len(self.pending) >= MAX_PENDING_INPUTS:
                self.dropped_states += len(self.pending)
                self.pending.clear()
                self.current_axes = tuple((axis, "idle") for axis in self.choices)
                self.release_pending = True
            self.pending.append(state)
        elif self.pending and self.pending[-1].axes == axes:
            self.pending[-1] = state
        self.axes = axes

    def is_ready(self) -> bool:
        """Report whether a client has connected and the session remains open."""
        with self.lock:
            return self.ready and not self.end and not self.closed

    def was_ended_by_user(self) -> bool:
        """Distinguish an explicit end request from a disconnected client."""
        with self.lock:
            return self.end_requested

    def enable_controls(self) -> None:
        """Allow input after model setup unless the session has already closed."""
        with self.lock:
            if not self.closed:
                self.controls_ready = True

    def finish(self) -> None:
        """Disable controls and clear queued motion while the recording finishes."""
        with self.lock:
            self.finishing = True
            self.controls_ready = False
            self.pending.clear()

    def frame(self, encoded: str) -> None:
        """Keep the latest preview within the encoded size limit."""
        if len(encoded) > MAX_PREVIEW_CHARACTERS:
            return
        with self.lock:
            if not self.closed:
                self.preview = encoded
                self.preview_sequence += 1

    def close(self, *, is_termination_confirmed: bool, failed: bool = False) -> None:
        """Clear private media and input, then publish the final termination status."""
        with self.lock:
            self.closed = True
            self.end = True
            self.preview = ""
            self.pending.clear()
            self.is_termination_confirmed = is_termination_confirmed
            self.failed = failed


def unavailable() -> ConnectorError:
    """Return a public error without revealing whether a private session exists."""
    return ConnectorError(ErrorCode.UNAVAILABLE, translate("main", "errors.liveSessionUnavailable"))
