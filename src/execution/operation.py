"""Define the validated model operation consumed by the shared session owner."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from .transport import Transport
    from .events import SessionEvents
    from ..settings.settings import Settings


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
        is_passthrough_enabled: Whether prompt changes continue to the provider immediately.
        audio_prompt: Text shown in the optional audio prompt control.
        is_audio_enabled: Whether the audio prompt control starts enabled.

    """

    prompt: str
    is_passthrough_enabled: bool = False
    audio_prompt: str = ""
    is_audio_enabled: bool = False


class VideoOperation(Protocol):
    """Own model commands while the session owns connection and media lifetime.

    Attributes:
        model_name: Provider connection name.
        fallback_fps: Frame rate used when the provider supplies no timing.
        requires_audio: Whether to save the provider recording with audio.

    """

    model_name: ClassVar[str]

    @property
    def prompt(self) -> str:
        """Return the opening prompt for the model request."""
        raise NotImplementedError

    @property
    def duration_seconds(self) -> float:
        """Return the requested generation duration in seconds."""
        raise NotImplementedError

    fallback_fps: ClassVar[int]
    requires_audio: ClassVar[bool]

    def build_control_values(self) -> ControlValues:
        """Return per-session values for optional live controls."""
        raise NotImplementedError

    def validate(self, settings: Settings) -> None:
        """Reject inputs that violate the model contract or configured execution limits."""
        raise NotImplementedError

    async def configure(
        self, transport: Transport, events: SessionEvents, max_capture_seconds: float
    ) -> RecordingWindow:
        """Start generation and return the provider recording interval to save."""
        raise NotImplementedError

    async def release(self, transport: Transport) -> None:
        """Release request-owned uploads or input tracks before the session closes."""
        raise NotImplementedError


__all__ = ["ControlValues", "RecordingWindow", "VideoOperation"]
