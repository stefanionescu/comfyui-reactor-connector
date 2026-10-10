"""Public recording facts."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from .documents import Json


@dataclass(frozen=True, slots=True)
class RunReport:
    """Recording facts that identify model and connector versions.

    Attributes:
        run_id: Unique identifier for this execution.
        node_id: Registered public node identifier.
        model_name: Provider model connection.
        requested_duration_seconds: Requested media duration.
        connector_version: Installed connector version.
        sdk_version: Installed Reactor SDK version.

    """

    run_id: str
    node_id: str
    model_name: str
    requested_duration_seconds: float
    connector_version: str
    sdk_version: str

    def to_json(self) -> dict[str, Json]:
        """Serialize public recording facts without prompts, credentials, or media inputs."""
        return {
            "schema_version": 1,
            "run_id": self.run_id,
            "node_id": self.node_id,
            "model_name": self.model_name,
            "requested_duration_seconds": self.requested_duration_seconds,
            "connector_version": self.connector_version,
            "sdk_version": self.sdk_version,
        }
