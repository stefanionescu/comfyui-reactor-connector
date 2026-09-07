"""Limit connector sessions fairly across ComfyUI executor event loops."""

import math
import time
import asyncio
import threading
from ..codes import ErrorCode
from collections import deque
from dataclasses import dataclass
from ..errors import ConnectorError
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from ...config.generation.session import MAX_SESSION_CAPACITY, DEFAULT_SESSION_CAPACITY


@dataclass(eq=False, slots=True)
class AdmissionTicket:
    """A wake-up event owned only by the loop that requested admission."""

    loop: asyncio.AbstractEventLoop
    changed: asyncio.Event


class SessionAdmission:
    """Protect a FIFO queue and signal each waiter through its own event loop."""

    def __init__(self, capacity: int = DEFAULT_SESSION_CAPACITY) -> None:
        """Create the shared queue with a validated concurrent-session limit."""
        if type(capacity) is not int or not 1 <= capacity <= MAX_SESSION_CAPACITY:
            msg = "Choose a session capacity from 1 to 4."
            raise ValueError(msg)
        self.capacity = capacity
        self._lock = threading.Lock()
        self._waiting: deque[AdmissionTicket] = deque()
        self._active: set[AdmissionTicket] = set()
        self._blocked_until = 0.0

    def block_for(self, seconds: float) -> None:
        """Reject new and queued runs while a previous session may remain active."""
        with self._lock:
            self._blocked_until = max(self._blocked_until, time.monotonic() + seconds)
            for ticket in self._waiting:
                ticket.loop.call_soon_threadsafe(ticket.changed.set)

    def counts(self) -> tuple[int, int]:
        """Return active and waiting counts without exposing run identities."""
        with self._lock:
            return len(self._active), len(self._waiting)

    def _notify(self) -> None:
        """Wake eligible waiters on their owning event loops while holding the queue lock."""
        for ticket in list(self._waiting)[: self.capacity - len(self._active)]:
            ticket.loop.call_soon_threadsafe(ticket.changed.set)

    def _claim(self, ticket: AdmissionTicket) -> bool:
        """Admit the first waiter when capacity and the cleanup deadline allow it."""
        with self._lock:
            remaining = self._blocked_until - time.monotonic()
            if remaining > 0:
                raise ConnectorError(
                    ErrorCode.CLEANUP,
                    "An earlier Reactor session has unconfirmed termination. "
                    f"Wait {math.ceil(remaining)} seconds before starting another run.",
                )
            if self._waiting[0] is ticket and len(self._active) < self.capacity:
                self._waiting.popleft()
                self._active.add(ticket)
                self._notify()
                return True
            ticket.changed.clear()
            return False

    @asynccontextmanager
    async def slot(self, timeout_seconds: float) -> AsyncGenerator[None, None]:
        """Acquire before client construction and release after all session cleanup."""
        ticket = AdmissionTicket(asyncio.get_running_loop(), asyncio.Event())
        with self._lock:
            self._waiting.append(ticket)
        try:
            try:
                async with asyncio.timeout(timeout_seconds):
                    while not self._claim(ticket):
                        await ticket.changed.wait()
            except TimeoutError:
                raise ConnectorError(
                    ErrorCode.TIMEOUT,
                    "Timed out waiting for another Reactor run to finish. This waiting run did not open a session.",
                ) from None
            yield
        finally:
            with self._lock:
                if ticket in self._waiting:
                    self._waiting.remove(ticket)
                self._active.discard(ticket)
                self._notify()
