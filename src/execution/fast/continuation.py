"""Chain a chosen number of Fast H3 clips in one session and save their sound."""

from ...language import translate
from ..transport import Transport
from ..events import SessionEvents
from ....config.nodes import MAX_SEED
from ...state.settings import Settings
from .generate import FastGenerateOperation
from ...state.session import RecordingWindow
from ...state.generation.fast import FastClip
from ...errors import ErrorCode, ConnectorError
from ...state.generation.fast import FastContinueRequest
from .clip import seconds, read_clip, FastClipEvents, message_payload
from ....config.generation.fast import (
    MAX_CLIP_COUNT,
    MIN_CLIP_COUNT,
    OPTIONS_ASPECT,
    MAX_CLIP_SECONDS,
    MIN_CLIP_SECONDS,
    MAX_PROMPT_CHARACTERS,
)


class FastContinueOperation(FastGenerateOperation):
    """Chain the requested clips while preserving their accepted media intervals.

    Attributes:
        sequence: Clip length, clip count, and later prompts for the chain.

    """

    def __init__(self, inputs: FastContinueRequest) -> None:
        """Keep the sequence settings that a single Fast H3 clip does not have."""
        super().__init__(inputs)
        self.sequence = inputs

    def _validate_clips(self, settings: Settings) -> None:
        """Check clip count, clip length, aspect ratio, and prompts for the whole chain."""
        del settings
        if (
            type(self.sequence.clip_count) is not int
            or not MIN_CLIP_COUNT <= self.sequence.clip_count <= MAX_CLIP_COUNT
        ):
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.clipCount"))
        if (
            type(self.sequence.clip_seconds) not in (int, float)
            or not MIN_CLIP_SECONDS <= self.sequence.clip_seconds <= MAX_CLIP_SECONDS
        ):
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.continuedClipDuration"))
        if self.sequence.aspect not in OPTIONS_ASPECT:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.aspectRatio"))
        prompts = (self.prompt, *self.sequence.later_prompts)
        if len(self.sequence.later_prompts) > self.sequence.clip_count - 1 or any(
            type(prompt) is not str or not prompt.strip() or len(prompt) > MAX_PROMPT_CHARACTERS for prompt in prompts
        ):
            raise ConnectorError(
                ErrorCode.INVALID_INPUT,
                translate("main", "errors.continuationPrompts"),
            )

    async def begin_generation(
        self, transport: Transport, events: SessionEvents, max_capture_seconds: float
    ) -> RecordingWindow:
        """Play linked clips and enough trailing media to finish the saved recording."""
        if not any(
            track.name == "main_audio" and track.kind == "audio" and track.direction == "recvonly"
            for track in transport.tracks
        ):
            raise ConnectorError(ErrorCode.UNAVAILABLE, translate("main", "errors.fastAudioMissing"))
        clips = FastClipEvents(events, limit=self.sequence.clip_count + 1)
        await events.command_reply("set_autoplay", {"enabled": False})
        await events.command_reply("set_flush_on_clip_end", {"enabled": False})
        await events.command_reply("set_canvas", {"aspect": self.sequence.aspect})
        state = await self._state(transport, events)
        minimum, maximum = (
            seconds(state.get("clip_seconds_min")),
            seconds(state.get("clip_seconds_max")),
        )
        if not minimum <= self.sequence.clip_seconds <= maximum:
            raise ConnectorError(
                ErrorCode.INVALID_INPUT,
                translate("main", "errors.clipDurationUnsupported"),
            )
        current = await self._enqueue(events, None, 0)
        self._validate_recording_limit(current, max_capture_seconds)
        await events.call("clip_build", clips.wait_ready(current))
        start_seconds = await self._read_playback_start(transport, events)
        await events.command_reply("set_autoplay", {"enabled": True})
        # Queue one continuation ahead. Each clip opens from the previous clip's last frame.
        for index in range(1, self.sequence.clip_count):
            following = await self._enqueue(events, current, index)
            self._validate_recording_limit(following, max_capture_seconds)
            await events.call("clip_playback", clips.wait_finished(current))
            current = following
        duration = await events.call("clip_playback", clips.wait_finished(current)) - start_seconds
        await events.command_reply("set_autoplay", {"enabled": False})
        if not 0 < duration <= max_capture_seconds:
            raise ConnectorError(
                ErrorCode.CAPTURE,
                (translate("main", "errors.sequenceCaptureLimit")),
            )
        events.model_timing.update(saved_start_seconds=start_seconds, saved_duration_seconds=duration)
        # The recorder needs later media to close its final fragment.
        tail = await self._enqueue(events, current, self.sequence.clip_count, duration=maximum)
        await events.call("recording_tail_build", clips.wait_ready(tail))
        await events.command_reply("play", {"clip_id": tail.clip_id})
        return RecordingWindow(start_seconds, duration)

    async def _read_playback_start(self, transport: Transport, events: SessionEvents) -> float:
        """Read the recording position only while automatic playback is stopped."""
        state = await self._state(transport, events)
        if state.get("playing") is not False:
            raise ConnectorError(ErrorCode.UNAVAILABLE, translate("main", "errors.sequencePlaybackOrder"))
        return seconds(state.get("seconds_sent"))

    def _validate_recording_limit(self, clip: FastClip, max_capture_seconds: float) -> None:
        """Reject an accepted clip length that would exceed the configured capture limit."""
        if clip.seconds * self.sequence.clip_count > max_capture_seconds:
            raise ConnectorError(
                ErrorCode.INVALID_INPUT,
                translate("main", "errors.acceptedSequenceLimit"),
            )

    async def _enqueue(
        self,
        events: SessionEvents,
        previous: FastClip | None,
        index: int,
        *,
        duration: float | None = None,
    ) -> FastClip:
        """Queue a clip from the starting image or the previous clip and validate its length."""
        prompt = (
            self.sequence.later_prompts[index - 1] if 0 < index <= len(self.sequence.later_prompts) else self.prompt
        )
        payload: dict[str, object] = {
            "prompt": prompt,
            "seconds": duration or self.sequence.clip_seconds,
            "seed": (self.sequence.seed + index) % (MAX_SEED + 1),
        }
        if previous is not None:
            payload["continue_from_clip_id"] = previous.clip_id
        elif self.sequence.image is not None:
            payload["starting_frame"] = await events.call(
                "upload",
                events.transport.upload_file(self.sequence.image, name="input.png", mime_type="image/png"),
            )
        reply = await events.command_reply("enqueue", payload)
        return read_clip(message_payload(reply, "clip_queued"))
