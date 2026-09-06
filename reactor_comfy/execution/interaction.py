"""Let a browser observer share one owned session without replacing its lifecycle."""

from typing import Protocol

from .events import SessionEvents
from .transport import Track, Transport


class SessionInteraction(Protocol):
    async def connected(
        self, transport: Transport, track: Track, events: SessionEvents
    ) -> None: ...

    def configured(self, *, video_started: bool) -> None: ...

    async def stop(self) -> None: ...

    def closed(self, *, termination_confirmed: bool, failed: bool) -> None: ...
