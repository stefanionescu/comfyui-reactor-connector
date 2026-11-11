"""Store browser leases and expire closed entries."""

import time
import threading
from dataclasses import field, dataclass

from .lease import BrowserLease
from ..errors import ErrorCode, ConnectorError
from ..config.live import MAX_STORED_SESSIONS, CLOSED_SESSION_RETENTION_SECONDS
from ..config.messages.live import LIVE_PANEL_LIMIT


@dataclass(slots=True)
class BrowserRegistry:
    """Limit stored browser sessions and expire closed sessions after the retention period.

    Attributes:
        lock: Guards the leases across server and executor threads.
        leases: Active and recently closed client sessions by lease identifier.

    """

    lock: threading.Lock = field(default_factory=threading.Lock)
    leases: dict[str, BrowserLease] = field(default_factory=dict[str, BrowserLease])

    def add(self, lease: BrowserLease) -> None:
        """Remove expired closed sessions before enforcing the stored-session limit.

        Args:
            lease: The lease to store.

        Raises:
            ConnectorError: When the registry already holds its limit of sessions.

        """
        with self.lock:
            self.leases = {
                key: value
                for key, value in self.leases.items()
                if not value.closed or time.monotonic() - value.last_seen < CLOSED_SESSION_RETENTION_SECONDS
            }
            if len(self.leases) >= MAX_STORED_SESSIONS:
                raise ConnectorError(ErrorCode.UNAVAILABLE, LIVE_PANEL_LIMIT)
            self.leases[lease.identifier] = lease
