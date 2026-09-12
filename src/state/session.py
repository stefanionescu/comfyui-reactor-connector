"""Session timing, admission, and outcome records."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from .reports import FailureReport
    from asyncio import Event, AbstractEventLoop


@dataclass(frozen=True, slots=True)
class RecordingWindow:
    """An interval selected from a provider recording.

    Attributes:
        start_seconds: Position where the saved interval begins.
        duration_seconds: Length of the saved interval.

    """

    start_seconds: float
    duration_seconds: float


@dataclass(frozen=True, slots=True)
class ControlValues:
    """Provider-neutral values used to construct optional browser controls.

    Attributes:
        prompt: Text shown in the live prompt control.
        is_passthrough_enabled: Whether to send prompts without preprocessing.
        audio_prompt: Text shown in the optional audio prompt control.
        is_audio_enabled: Whether the audio prompt control starts enabled.

    """

    prompt: str
    is_passthrough_enabled: bool = False
    audio_prompt: str = ""
    is_audio_enabled: bool = False


@dataclass(slots=True)
class SessionOutcome:
    """Termination facts used to decide whether another session may start.

    Attributes:
        is_connection_attempted: Whether provider setup began.
        is_termination_confirmed: Whether the provider confirmed termination.
        diagnostic: Optional private failure details.

    """

    is_connection_attempted: bool = False
    is_termination_confirmed: bool = False
    diagnostic: FailureReport | None = None

    @property
    def is_termination_uncertain(self) -> bool:
        """Report whether a connection was attempted without confirmed termination."""
        return self.is_connection_attempted and not self.is_termination_confirmed


@dataclass(eq=False, slots=True)
class AdmissionTicket:
    """A wake-up event owned by the loop requesting admission.

    Attributes:
        loop: Requesting event loop.
        changed: Admission-change notification for that loop.

    """

    loop: AbstractEventLoop
    changed: Event


__all__ = ["AdmissionTicket", "ControlValues", "RecordingWindow", "SessionOutcome"]
