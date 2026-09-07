"""Let a browser observer share one owned session without replacing its lifecycle."""

from typing import Protocol
from .events import SessionEvents
from .transport import Track, Transport


class SessionInteraction(Protocol):
    """Session lifecycle callbacks used by the submitting client's live controls."""

    async def connected(self, transport: Transport, track: Track, events: SessionEvents) -> None:
        """Attach live controls to the connected transport, output track, and session events."""
        # codeql[py/ineffectual-statement] -- reason: Protocol method declaration.
        ...

    def configured(self, *, video_started: bool) -> None:
        """Mark the model ready for live actions and identify whether video has started."""
        # codeql[py/ineffectual-statement] -- reason: Protocol method declaration.
        ...

    async def stop(self) -> None:
        """Stop owned control tasks before session cleanup completes."""
        # codeql[py/ineffectual-statement] -- reason: Protocol method declaration.
        ...

    def closed(self, *, termination_confirmed: bool, failed: bool) -> None:
        """Record whether remote termination was confirmed and whether execution failed."""
        # codeql[py/ineffectual-statement] -- reason: Protocol method declaration.
        ...
