"""Resources and termination state owned by one generation session."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from asyncio import Task
    from ..events import SessionEvents
    from ..operation import VideoOperation
    from ..diagnostics import FailureReport
    from ...media.state import CaptureResult
    from ..transport import Track, Transport
    from ...media.capture import VideoCapture
    from ...settings.settings import Settings
    from ..interaction import SessionInteraction


@dataclass(slots=True)
class SessionOutcome:
    """Facts used by the host to decide whether another session may start."""

    is_connection_attempted: bool = False
    is_termination_confirmed: bool = False
    diagnostic: FailureReport | None = None

    @property
    def is_termination_uncertain(self) -> bool:
        """Report whether a connection was attempted without confirmed termination."""
        return self.is_connection_attempted and not self.is_termination_confirmed


@dataclass(slots=True, repr=False)
class SessionResources:
    """Resources owned by one generation and released together before the session finishes."""

    request: VideoOperation
    transport: Transport
    settings: Settings
    capture: VideoCapture
    events: SessionEvents
    worker: Task[CaptureResult]
    outcome: SessionOutcome
    interaction: SessionInteraction | None
    track: Track | None = None


__all__ = ["SessionOutcome", "SessionResources"]
