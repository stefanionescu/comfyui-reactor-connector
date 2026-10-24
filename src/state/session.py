"""Session timing and outcome records."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RecordingWindow:
    """An interval selected from a provider recording.

    Attributes:
        start_seconds: Position where the saved interval begins.
        duration_seconds: Length of the saved interval.

    """

    start_seconds: float
    duration_seconds: float


@dataclass(slots=True)
class SessionOutcome:
    """Termination facts that session cleanup reports.

    Attributes:
        is_connection_attempted: Whether provider setup began.
        is_termination_confirmed: Whether the provider confirmed termination.

    """

    is_connection_attempted: bool = False
    is_termination_confirmed: bool = False
