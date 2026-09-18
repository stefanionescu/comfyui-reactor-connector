"""Store browser leases and expire closed entries."""

import time
import threading
from ..state.documents import Json
from .lease import unavailable, BrowserLease
from ..errors import ErrorCode, ConnectorError
from ..config.messages.live import LIVE_PANEL_LIMIT
from ..config.live import MAX_STORED_SESSIONS, CLOSED_SESSION_RETENTION_SECONDS


class BrowserRegistry:
    """Limit stored browser sessions and expire closed sessions after the retention period."""

    def __init__(self) -> None:
        """Create a locked collection of active and recently closed client sessions."""
        self.lock = threading.Lock()
        self.leases: dict[str, BrowserLease] = {}

    def add(self, lease: BrowserLease) -> None:
        """Remove expired closed sessions before enforcing the stored-session limit."""
        with self.lock:
            self.leases = {
                key: value
                for key, value in self.leases.items()
                if not value.closed or time.monotonic() - value.last_seen < CLOSED_SESSION_RETENTION_SECONDS
            }
            if len(self.leases) >= MAX_STORED_SESSIONS:
                raise ConnectorError(ErrorCode.UNAVAILABLE, LIVE_PANEL_LIMIT)
            self.leases[lease.identifier] = lease

    def exchange(self, document: dict[str, Json]) -> dict[str, Json]:
        """Find the requested session and delegate its capability and input checks."""
        identifier = document.get("lease")
        with self.lock:
            lease = self.leases.get(identifier) if isinstance(identifier, str) else None
        if lease is None:
            raise unavailable()
        return lease.exchange(document)
