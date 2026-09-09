"""Chain a chosen number of Fast H3 clips in one session and save their sound."""

from ..inputs import VideoInputs
from ...language import translate
from ..transport import Transport
from dataclasses import dataclass
from ..events import SessionEvents
from ...settings.settings import Settings
from .generate import FastGenerateRequest
from ...errors import ErrorCode, ConnectorError
from .clip import seconds, FastClip, FastClipEvents, message_payload
from ....config.generation.fast import (
    MAX_CLIP_COUNT,
    MIN_CLIP_COUNT,
    MAX_CLIP_SECONDS,
    MIN_CLIP_SECONDS,
    MAX_PROMPT_CHARACTERS,
)


@dataclass(frozen=True, slots=True)
class FastContinueRequest(FastGenerateRequest):
    """A sequence of Fast H3 clips linked by their final frames."""

    clip_seconds: float = 6
    clip_count: int = 3
    later_prompts: tuple[str, ...] = ()

    def validate(self, settings: Settings) -> None:
        """Check sequence length, prompts, and upload limits before starting a session."""
        VideoInputs.validate(self, settings)
        if type(self.clip_count) is not int or not MIN_CLIP_COUNT <= self.clip_count <= MAX_CLIP_COUNT:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.clipCount"))
        if type(self.clip_seconds) not in (int, float) or not MIN_CLIP_SECONDS <= self.clip_seconds <= MAX_CLIP_SECONDS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.continuedClipDuration"))
        if self.aspect not in ("16:9", "1:1", "9:16", "4:3"):
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.aspectRatio"))
        prompts = (self.prompt, *self.later_prompts)
        if len(self.later_prompts) > self.clip_count - 1 or any(
            type(prompt) is not str or not prompt.strip() or len(prompt) > MAX_PROMPT_CHARACTERS for prompt in prompts
        ):
            raise ConnectorError(
                ErrorCode.INVALID_INPUT,
                translate("main", "errors.continuationPrompts"),
            )
        self.recording.maximum_seconds = settings.max_capture_seconds

    async def configure(self, transport: Transport, events: SessionEvents) -> None:
        """Play linked clips and enough trailing media to finish the saved recording."""
        if not any(
            track.name == "main_audio" and track.kind == "audio" and track.direction == "recvonly"
            for track in transport.tracks
        ):
            raise ConnectorError(ErrorCode.UNAVAILABLE, translate("main", "errors.fastAudioMissing"))
        clips = FastClipEvents(events, limit=self.clip_count + 1)
        await events.command("set_autoplay", {"enabled": False})
        await events.command("set_flush_on_clip_end", {"enabled": False})
        await events.command("set_canvas", {"aspect": self.aspect})
        state = await self._state(transport, events)
        minimum, maximum = (
            seconds(state.get("clip_seconds_min")),
            seconds(state.get("clip_seconds_max")),
        )
        if not minimum <= self.clip_seconds <= maximum:
            raise ConnectorError(
                ErrorCode.INVALID_INPUT,
                translate("main", "errors.clipDurationUnsupported"),
            )
        current = await self._enqueue(events, None, 0)
        await events.call("clip_build", clips.wait_ready(current))
        state = await self._state(transport, events)
        if state.get("playing") is not False:
            raise ConnectorError(ErrorCode.UNAVAILABLE, translate("main", "errors.sequencePlaybackOrder"))
        self.recording.start_seconds = seconds(state.get("seconds_sent"))
        await events.command("set_autoplay", {"enabled": True})
        # Queue one continuation ahead. Each clip opens from the previous clip's last frame.
        for index in range(1, self.clip_count):
            following = await self._enqueue(events, current, index)
            await events.call("clip_playback", clips.wait_finished(current))
            current = following
        duration = await events.call("clip_playback", clips.wait_finished(current)) - self.recording.start_seconds
        await events.command("set_autoplay", {"enabled": False})
        if not 0 < duration <= self.recording.maximum_seconds:
            raise ConnectorError(
                ErrorCode.CAPTURE,
                (translate("main", "errors.sequenceCaptureLimit")),
            )
        self.recording.duration_seconds = duration
        events.model_timing.update(saved_start_seconds=self.recording.start_seconds, saved_duration_seconds=duration)
        # The recorder needs later media to close its final fragment.
        tail = await self._enqueue(events, current, self.clip_count, duration=maximum)
        await events.call("recording_tail_build", clips.wait_ready(tail))
        await events.command("play", {"clip_id": tail.clip_id})

    async def _enqueue(
        self,
        events: SessionEvents,
        previous: FastClip | None,
        index: int,
        *,
        duration: float | None = None,
    ) -> FastClip:
        """Queue a clip from the starting image or the previous clip and validate its length."""
        prompt = self.later_prompts[index - 1] if 0 < index <= len(self.later_prompts) else self.prompt
        payload: dict[str, object] = {
            "prompt": prompt,
            "seconds": duration or self.clip_seconds,
            "seed": (self.seed + index) % 2**32,
        }
        if previous is not None:
            payload["continue_from_clip_id"] = previous.clip_id
        elif self.image is not None:
            payload["starting_frame"] = await events.call(
                "upload",
                events.transport.upload_file(self.image, name="input.png", mime_type="image/png"),
            )
        reply = await events.command_reply("enqueue", payload)
        clip = FastClip.read(message_payload(reply, "clip_queued"))
        if duration is None and clip.seconds * self.clip_count > self.recording.maximum_seconds:
            raise ConnectorError(
                ErrorCode.INVALID_INPUT,
                translate("main", "errors.acceptedSequenceLimit"),
            )
        return clip
