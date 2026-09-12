"""Live resources that one session releases together."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from asyncio import Task
    from ..events import SessionEvents
    from ...state.settings import Settings
    from ..operation import VideoOperation
    from ...state.media import CaptureResult
    from ..transport import Track, Transport
    from ...media.capture import VideoCapture
    from ...state.session import SessionOutcome
    from ..interaction import SessionInteraction


@dataclass(slots=True, repr=False)
class SessionResources:
    """Resources released together before the owning session finishes.

    Attributes:
        request: Model operation being executed.
        transport: Provider connection.
        settings: Effective server limits.
        capture: Incremental media capture owner.
        events: Provider event subscription owner.
        worker: Capture task.
        outcome: Shared termination facts.
        interaction: Optional live-control interaction.
        track: Selected provider media track.

    """

    request: VideoOperation
    transport: Transport
    settings: Settings
    capture: VideoCapture
    events: SessionEvents
    worker: Task[CaptureResult]
    outcome: SessionOutcome
    interaction: SessionInteraction | None
    track: Track | None = None


__all__ = ["SessionResources"]
