"""Execution settings and private configuration snapshot records."""

from .documents import Json
from .credentials import Credential
from dataclasses import field, asdict, dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    """Host limits that a workflow cannot increase.

    Attributes:
        max_capture_seconds: Maximum retained recording duration.
        max_session_seconds: Maximum remote session lifetime.
        connect_timeout_seconds: Connection setup deadline.
        first_frame_timeout_seconds: Deadline for the first generated frame.
        cleanup_timeout_seconds: Remote cleanup deadline.
        queue_timeout_seconds: Provider admission deadline.
        max_upload_megabytes: Maximum source upload size.
        max_capture_megabytes: Maximum retained recording size.
        max_queue_megabytes: Maximum buffered media size.
        catalog_interval_hours: Interval between public metadata checks.
        catalog_auto_check: Whether public metadata checks are enabled.

    """

    max_capture_seconds: int
    max_session_seconds: int
    connect_timeout_seconds: int
    first_frame_timeout_seconds: int
    cleanup_timeout_seconds: int
    queue_timeout_seconds: int
    max_upload_megabytes: int
    max_capture_megabytes: int
    max_queue_megabytes: int
    catalog_interval_hours: int
    catalog_auto_check: bool

    def to_json(self) -> dict[str, Json]:
        """Return only non-secret settings for the local configuration route."""
        return dict(asdict(self).items())


@dataclass(frozen=True, slots=True)
class ExecutionConfiguration:
    """One private settings and credential snapshot for an admitted operation.

    Attributes:
        settings: Effective execution limits and preferences.
        credential: Private provider credential excluded from representations.
        generation: Token identifying the effective execution configuration.

    """

    settings: Settings
    credential: Credential = field(repr=False)
    generation: str


__all__ = ["ExecutionConfiguration", "Settings"]
