"""Validate Fast H3 clip replies and observe one clip's lifecycle."""

from __future__ import annotations

import math
from uuid import UUID
from typing import TYPE_CHECKING, cast
import asyncio

from ...errors import ErrorCode, ConnectorError
from ...state.generation.fast import FastClip
from ...config.generation.fast import FRAME_RATE, MAX_CLIP_FRAMES, MAX_QUEUED_CLIPS, MAX_MEDIA_SECONDS
from ...config.messages.inputs import (
    CLIP_REPLY,
    CLIP_LENGTH,
    CLIP_MISSING,
    CLIP_IDENTIFIER,
    CLIP_MEDIA_TIME,
    CLIP_UNFINISHED,
    CLIPS_UNEXPECTED,
    CLIP_LENGTH_CHANGED,
    ACCEPTED_CLIP_CHANGED,
)

if TYPE_CHECKING:
    from ..events import SessionEvents


def read_clip(payload: dict[str, object]) -> FastClip:
    """Validate the clip identity, readiness, and agreement between duration and frame count.

    Args:
        payload: The reply data that holds the clip.

    Returns:
        The validated clip.

    Raises:
        ConnectorError: When the clip is missing or a field is invalid.

    """
    raw = payload.get('clip')
    if not isinstance(raw, dict):
        raise ConnectorError(ErrorCode.UNAVAILABLE, CLIP_MISSING)
    clip = cast('dict[str, object]', raw)
    identity, frames, ready = clip.get('clip_id'), clip.get('frames'), clip.get('ready')
    duration = seconds(clip.get('seconds'))
    if not isinstance(identity, str):
        raise ConnectorError(ErrorCode.UNAVAILABLE, CLIP_IDENTIFIER)
    try:
        canonical = str(UUID(identity))
    except ValueError:
        raise ConnectorError(ErrorCode.UNAVAILABLE, CLIP_IDENTIFIER) from None
    if canonical != identity:
        raise ConnectorError(ErrorCode.UNAVAILABLE, CLIP_IDENTIFIER)
    if (
        type(frames) not in (int, float)
        or not 1 <= cast('float', frames) <= MAX_CLIP_FRAMES
        or int(cast('float', frames)) != frames
        or type(ready) is not bool
        or not math.isclose(duration, cast('float', frames) / FRAME_RATE, abs_tol=0.001)
    ):
        raise ConnectorError(ErrorCode.UNAVAILABLE, CLIP_LENGTH)
    count = int(cast('float', frames))
    return FastClip(identity, count / FRAME_RATE, count, ready)


class FastClipEvents:
    """Limit stored clip updates; let the session remove the event handler."""

    def __init__(self, events: SessionEvents, *, limit: int = MAX_QUEUED_CLIPS) -> None:
        """Subscribe to clip updates with a fixed maximum number of stored clips.

        Args:
            events: The session events that deliver messages and failures.
            limit: The largest number of clips to store.

        """
        self.events = events
        self.limit = limit
        self.finished_at: dict[str, float] = {}
        self.playback_changed = asyncio.Event()
        self.clips: dict[str, FastClip] = {}
        self.generated = asyncio.Event()
        self.finished = asyncio.Event()
        self.clip_id: str | None = None
        self.end_seconds: float | None = None
        events.transport.on('message', self.observe)
        events.handlers.append(('message', self.observe))

    def observe(self, message: object) -> None:
        """Record relevant clip updates and forward invalid replies to the session failure signal.

        Args:
            message: The SDK message to inspect.

        """
        if not isinstance(message, dict):
            return
        envelope = cast('dict[str, object]', message)
        kind = envelope.get('type')
        if kind not in ('clip_generated', 'clip_finished', 'clip_failed', 'clip_stopped'):
            return
        try:
            self._record_clip(envelope, str(kind))
        except ConnectorError as error:
            self.events.on_error(error)

    def _record_clip(self, envelope: dict[str, object], kind: str) -> None:
        """Validate a clip update and advance generation or playback signals.

        Args:
            envelope: The message that holds the clip update.
            kind: The type of the clip update.

        Raises:
            ConnectorError: When the clip failed, stopped, or exceeds the stored limit.

        """
        if kind in ('clip_failed', 'clip_stopped'):
            raise ConnectorError(ErrorCode.CAPTURE, CLIP_UNFINISHED)
        clip = read_clip(message_payload(envelope, str(kind)))
        if len(self.clips) >= self.limit and clip.clip_id not in self.clips:
            raise ConnectorError(ErrorCode.UNAVAILABLE, CLIPS_UNEXPECTED)
        self.clips[clip.clip_id] = clip
        if kind == 'clip_generated':
            self.generated.set()
        else:
            self.finished_at[clip.clip_id] = seconds(message_payload(envelope, 'clip_finished').get('seconds_sent'))
            self.playback_changed.set()
        if kind == 'clip_finished' and clip.clip_id == self.clip_id:
            self.end_seconds = seconds(message_payload(envelope, 'clip_finished').get('seconds_sent'))
            self.finished.set()

    async def wait_ready(self, clip: FastClip) -> None:
        """Wait for generation without accepting changes to the queued clip length.

        Args:
            clip: The queued clip to wait for.

        Raises:
            ConnectorError: When the model changes the length of the clip.

        """
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
                    CLIP_LENGTH_CHANGED,
                )

    async def wait_finished(self, clip: FastClip) -> float:
        """Wait for playback and return its reported end time after checking the clip length.

        Args:
            clip: The accepted clip whose playback to wait for.

        Returns:
            The media time at which playback finished, in seconds.

        Raises:
            ConnectorError: When the reported clip differs from the accepted one.

        """
        while clip.clip_id not in self.finished_at:
            self.playback_changed.clear()
            await self.playback_changed.wait()
        reported = self.clips.get(clip.clip_id)
        if reported is None or reported.frames != clip.frames:
            raise ConnectorError(ErrorCode.CAPTURE, ACCEPTED_CLIP_CHANGED)
        return self.finished_at[clip.clip_id]


def message_payload(message: object, kind: str) -> dict[str, object]:
    """Require a matching message type and an object payload.

    Args:
        message: The reply or event to read.
        kind: The message type to require.

    Returns:
        The data object of the message.

    Raises:
        ConnectorError: When the type differs or the data is not an object.

    """
    if isinstance(message, dict):
        envelope = cast('dict[str, object]', message)
        payload = envelope.get('data')
        if envelope.get('type') == kind and isinstance(payload, dict):
            return cast('dict[str, object]', payload)
    raise ConnectorError(ErrorCode.UNAVAILABLE, CLIP_REPLY)


def seconds(value: object) -> float:
    """Validate a provider media time before using it to select a recording interval.

    Args:
        value: The media time that the provider reported.

    Returns:
        The media time as a float, in seconds.

    Raises:
        ConnectorError: When the value is not a number in the accepted range.

    """
    if type(value) not in (int, float) or not 0 <= cast('float', value) <= MAX_MEDIA_SECONDS:
        raise ConnectorError(ErrorCode.UNAVAILABLE, CLIP_MEDIA_TIME)
    return float(cast('float', value))
