"""Current and previous model metadata held by the discovery store."""

import hashlib
from .contracts import Snapshot
from ..serialization import Json
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ModelState:
    """The current public snapshot and one optional rollback snapshot."""

    current: Snapshot | None = None
    previous: Snapshot | None = None

    @property
    def revision(self) -> str:
        """Identify the cached metadata or the state before the first refresh."""
        return self.current.revision if self.current else hashlib.sha256(b"null").hexdigest()

    def to_json(self) -> dict[str, Json]:
        """Serialize both snapshots in the versioned local storage format."""
        return {
            "version": 1,
            "current": self.current.to_json() if self.current else None,
            "previous": self.previous.to_json() if self.previous else None,
        }


__all__ = ["ModelState"]
