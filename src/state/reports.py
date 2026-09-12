"""Public recording facts and private failure records."""

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


@dataclass(frozen=True, slots=True, repr=False)
class FailureReport:
    """Private provider error details separated from public exceptions.

    Attributes:
        phase: Operation that failed.
        code: Bounded provider or connector error code.
        message: Bounded private error message.

    """

    phase: str
    code: str
    message: str

    def __repr__(self) -> str:
        """Hide private failure details from object representations."""
        return "FailureReport(<private>)"


__all__ = ["FailureReport", "RunReport"]
