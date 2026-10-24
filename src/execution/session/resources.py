"""Live resources that one session releases together."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from asyncio import Task

    from reactor_sdk import Track

    from ..events import SessionEvents
    from ..inputs import VideoOperation
    from ..transport import SessionTransport
    from ..interaction import SessionInteraction
    from ...state.media import CaptureResult
    from ...media.capture import VideoCapture
    from ...state.session import SessionOutcome
    from ...state.settings import Settings


@dataclass(slots=True, repr=False)
class SessionResources:
    """Resources released together before the owning session finishes.

    Attributes:
        operation: Model operation that the session runs.
        transport: Provider connection.
        settings: Effective server limits.
        capture: Incremental media capture owner.
        events: Provider event subscription owner.
        worker: Capture task.

        outcome: Shared termination facts.
        interaction: Optional live-control interaction.
        track: Selected provider media track.

    """

    operation: VideoOperation
    transport: SessionTransport
    settings: Settings
    capture: VideoCapture
    events: SessionEvents
    worker: Task[CaptureResult]
    outcome: SessionOutcome
    interaction: SessionInteraction | None
    track: Track | None = None
