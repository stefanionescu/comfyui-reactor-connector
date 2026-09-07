"""Validate Fast H3 clip replies and observe one clip's lifecycle."""

from __future__ import annotations

import json
import math
import asyncio
from uuid import UUID
from ...codes import ErrorCode
from dataclasses import dataclass
from ...errors import ConnectorError
from typing import cast, TYPE_CHECKING
from ....config.generation.fast import MAX_CLIP_FRAMES, MAX_QUEUED_CLIPS, MAX_MEDIA_SECONDS

if TYPE_CHECKING:
    from ..events import SessionEvents


def message_payload(message: object, kind: str) -> dict[str, object]:
    """Require a matching message type and an object payload."""
    if isinstance(message, dict):
        envelope = cast("dict[str, object]", message)
        payload = envelope.get("data")
        if envelope.get("type") == kind and isinstance(payload, dict):
            return cast("dict[str, object]", payload)
    raise ConnectorError(ErrorCode.UNAVAILABLE, "Fast H3 returned an unexpected reply.")


def seconds(value: object) -> float:
    """Validate a provider media time before using it to select a recording interval."""
    if type(value) not in (int, float) or not 0 <= cast("float", value) <= MAX_MEDIA_SECONDS:
        raise ConnectorError(ErrorCode.UNAVAILABLE, "Fast H3 returned an invalid media time.")
    return float(cast("float", value))


@dataclass(frozen=True, slots=True)
class FastClip:
    """A generated Fast H3 clip and its reported frame count, duration, and readiness."""

    clip_id: str
    seconds: float
    frames: int
    ready: bool

    @classmethod
    def read(cls, payload: dict[str, object]) -> FastClip:
        """Validate the clip identity, readiness, and agreement between duration and frame count."""
        raw = payload.get("clip")
        if not isinstance(raw, dict):
            raise ConnectorError(ErrorCode.UNAVAILABLE, "Fast H3 did not return a clip.")
        clip = cast("dict[str, object]", raw)
        identity, frames, ready = clip.get("clip_id"), clip.get("frames"), clip.get("ready")
        duration = seconds(clip.get("seconds"))
        if not isinstance(identity, str):
            raise ConnectorError(ErrorCode.UNAVAILABLE, "Fast H3 returned an invalid clip ID.")
        try:
            canonical = str(UUID(identity))
        except ValueError:
            raise ConnectorError(ErrorCode.UNAVAILABLE, "Fast H3 returned an invalid clip ID.") from None
        if canonical != identity:
            raise ConnectorError(ErrorCode.UNAVAILABLE, "Fast H3 returned an invalid clip ID.")
        if (
            type(frames) not in (int, float)
            or not 1 <= cast("float", frames) <= MAX_CLIP_FRAMES
            or int(cast("float", frames)) != frames
            or type(ready) is not bool
            or not math.isclose(duration, cast("float", frames) / 24, abs_tol=0.001)
        ):
            raise ConnectorError(
                ErrorCode.UNAVAILABLE,
                "Fast H3 returned an invalid clip length.",
                diagnostic_detail=json.dumps(
                    {
                        "frames_type": type(frames).__name__,
                        "frames": frames if type(frames) in (int, float) else None,
                        "seconds": duration,
                        "ready_type": type(ready).__name__,
                    }
                ),
            )
        count = int(cast("float", frames))
        return cls(identity, count / 24, count, ready)


class FastClipEvents:
    """Limit stored clip updates; let the session remove the event handler."""

    def __init__(self, events: SessionEvents, *, limit: int = MAX_QUEUED_CLIPS) -> None:
        """Subscribe to clip updates with a fixed maximum number of stored clips."""
        self.events = events
        self.limit = limit
        self.finished_at: dict[str, float] = {}
        self.playback_changed = asyncio.Event()
        self.clips: dict[str, FastClip] = {}
        self.generated = asyncio.Event()
        self.finished = asyncio.Event()
        self.clip_id: str | None = None
        self.end_seconds: float | None = None
        events.transport.on("message", self.observe)
        events.handlers.append(("message", self.observe))

    def observe(self, message: object) -> None:
        """Record relevant clip updates and forward invalid replies to the session failure signal."""
        if not isinstance(message, dict):
            return
        envelope = cast("dict[str, object]", message)
        kind = envelope.get("type")
        if kind not in ("clip_generated", "clip_finished", "clip_failed", "clip_stopped"):
            return
        try:
            self._record_clip(envelope, str(kind))
        except ConnectorError as error:
            self.events.on_error(error)

    def _record_clip(self, envelope: dict[str, object], kind: str) -> None:
        """Validate a clip update and advance generation or playback signals."""
        if kind in ("clip_failed", "clip_stopped"):
            raise ConnectorError(ErrorCode.CAPTURE, "Fast H3 did not finish the queued clip.")
        clip = FastClip.read(message_payload(envelope, str(kind)))
        if len(self.clips) >= self.limit and clip.clip_id not in self.clips:
            raise ConnectorError(ErrorCode.UNAVAILABLE, "Fast H3 returned unexpected clips.")
        self.clips[clip.clip_id] = clip
        if kind == "clip_generated":
            self.generated.set()
        else:
            self.finished_at[clip.clip_id] = seconds(message_payload(envelope, "clip_finished").get("seconds_sent"))
            self.playback_changed.set()
        if kind == "clip_finished" and clip.clip_id == self.clip_id:
            self.end_seconds = seconds(message_payload(envelope, "clip_finished").get("seconds_sent"))
            self.events.model_timing["finished_clips"] = self.events.model_timing.get("finished_clips", 0) + 1
            self.events.model_timing["last_clip_end_seconds"] = self.end_seconds
            self.finished.set()

    async def wait_ready(self, clip: FastClip) -> None:
        """Wait for generation without accepting changes to the queued clip length."""
        self.clip_id = clip.clip_id
        self.finished.clear()
        self.end_seconds = None
        expected = clip
        while not clip.ready:
            await self.generated.wait()
            self.generated.clear()
            clip = self.clips.get(clip.clip_id, clip)
            if clip.frames != expected.frames or clip.seconds != expected.seconds:
                raise ConnectorError(
                    ErrorCode.UNAVAILABLE,
                    "Fast H3 changed the accepted clip length before playback.",
                )

    async def wait_finished(self, clip: FastClip) -> float:
        """Wait for playback and return its reported end time after checking the clip length."""
        while clip.clip_id not in self.finished_at:
            self.playback_changed.clear()
            await self.playback_changed.wait()
        reported = self.clips.get(clip.clip_id)
        if reported is None or reported.frames != clip.frames:
            raise ConnectorError(ErrorCode.CAPTURE, "Fast H3 changed a clip's accepted length.")
        return self.finished_at[clip.clip_id]
