"""Let a browser observer share one owned session without replacing its lifecycle."""

from typing import Protocol
from .events import SessionEvents
from collections.abc import Callable
from .transport import Track, Transport


class SessionInteraction(Protocol):
    """Session lifecycle callbacks used by the submitting client's live controls."""

    async def connected(self, transport: Transport, track: Track, events: SessionEvents) -> None:
        """Attach live controls to the connected transport, output track, and session events."""
        raise NotImplementedError

    def configured(self, *, video_started: bool) -> None:
        """Mark the model ready for live actions and identify whether video has started."""
        raise NotImplementedError

    async def stop(self) -> None:
        """Stop owned control tasks before session cleanup completes."""
        raise NotImplementedError

    def closed(self, *, is_termination_confirmed: bool, failed: bool) -> None:
        """Record whether remote termination was confirmed and whether execution failed."""
        raise NotImplementedError


class FramePublisher(Protocol):
    """Publish input frames for an operation and release them during cleanup."""

    async def begin(self, track: Track, fail: Callable[[object], None]) -> None:
        """Start publishing frames and report failures to the session owner."""
        raise NotImplementedError

    async def close(self) -> None:
        """Stop publication and release retained frames."""
        raise NotImplementedError
