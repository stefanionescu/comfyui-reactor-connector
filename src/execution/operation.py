"""Define the validated model operation consumed by the shared session owner."""

from .transport import Transport
from .events import SessionEvents
from typing import ClassVar, Protocol
from ..settings.settings import Settings


class VideoOperation(Protocol):
    """Own model commands while the runner owns connection and media lifetime."""

    model_name: ClassVar[str]

    @property
    def prompt(self) -> str:
        """Return the opening prompt for the model request."""
        # codeql[py/ineffectual-statement] -- reason: Protocol method declaration.
        ...

    @property
    def duration_seconds(self) -> float:
        """Return the requested generation duration in seconds."""
        # codeql[py/ineffectual-statement] -- reason: Protocol method declaration.
        ...

    fallback_fps: ClassVar[int]
    requires_audio: ClassVar[bool]

    @property
    def recording_start_seconds(self) -> float:
        """Return the start of the interval to keep from the session recording."""
        # codeql[py/ineffectual-statement] -- reason: Protocol method declaration.
        ...

    @property
    def recording_duration_seconds(self) -> float:
        """Return the duration to keep from the session recording."""
        # codeql[py/ineffectual-statement] -- reason: Protocol method declaration.
        ...

    def validate(self, settings: Settings) -> None:
        """Reject inputs that violate the model contract or configured execution limits."""
        # codeql[py/ineffectual-statement] -- reason: Protocol method declaration.
        ...

    async def configure(self, transport: Transport, events: SessionEvents) -> None:
        """Set the model inputs and start generation through the observed transport."""
        # codeql[py/ineffectual-statement] -- reason: Protocol method declaration.
        ...

    async def release(self, transport: Transport) -> None:
        """Release request-owned uploads or input tracks before the session closes."""
        # codeql[py/ineffectual-statement] -- reason: Protocol method declaration.
        ...
