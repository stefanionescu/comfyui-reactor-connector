"""Define the validated model operation consumed by the shared session owner."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Protocol

from .transport import Transport
from .events import SessionEvents
from ..settings.settings import Settings

if TYPE_CHECKING:
    from ..live.state import LiveOptions
    from ..media.webcam import WebcamFrames


@dataclass(frozen=True, slots=True)
class RecordingWindow:
    """An interval selected from a provider recording.

    Attributes:
        start_seconds: Position where the saved interval begins.
        duration_seconds: Length of the saved interval.
    """

    start_seconds: float
    duration_seconds: float


class VideoOperation(Protocol):
    """Own model commands while the runner owns connection and media lifetime."""

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

    def live_options(self, *, webcam: WebcamFrames | None = None) -> LiveOptions:
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


__all__ = ["RecordingWindow", "VideoOperation"]
