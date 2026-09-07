"""Keep one running session's transport, capture, and cleanup state together."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from asyncio import Task
    from ..events import SessionEvents
    from ..outcome import SessionOutcome
    from ..operation import VideoOperation
    from ..transport import Track, Transport
    from ...settings.settings import Settings
    from ..interaction import SessionInteraction
    from ...media.capture import VideoCapture, CaptureResult


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
