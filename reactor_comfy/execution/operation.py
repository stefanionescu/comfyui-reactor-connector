"""Define the validated model operation consumed by the shared session owner."""

from typing import ClassVar, Protocol

from ..config import Settings
from .events import SessionEvents
from .transport import Transport


class VideoOperation(Protocol):
    """Own model commands while the runner owns connection and media lifetime."""

    model_name: ClassVar[str]

    @property
    def prompt(self) -> str: ...

    @property
    def duration_seconds(self) -> float: ...

    fallback_fps: ClassVar[int]
    requires_audio: ClassVar[bool]

    @property
    def recording_start_seconds(self) -> float: ...

    @property
    def recording_duration_seconds(self) -> float: ...

    def validate(self, settings: Settings) -> None: ...

    async def configure(self, transport: Transport, events: SessionEvents) -> None: ...

    async def release(self, transport: Transport) -> None: ...
