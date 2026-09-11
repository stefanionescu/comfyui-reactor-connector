"""Build and play one Fast H3 clip with its accepted duration and native sound."""

import json
from typing import ClassVar
from ...models import MODELS
from ..inputs import VideoInputs
from ...language import translate
from ..transport import Transport
from dataclasses import dataclass
from ..events import SessionEvents
from ...settings.schema import Settings
from ..operation import RecordingWindow
from ...errors import ErrorCode, ConnectorError
from ...media.units import convert_mebibytes_to_bytes
from .clip import seconds, FastClip, FastClipEvents, message_payload
from ....config.generation.fast import (
    FRAME_RATE,
    DEFAULT_ASPECT,
    OPTIONS_ASPECT,
    MAX_CLIP_SECONDS,
    MIN_CLIP_SECONDS,
    MAX_PROMPT_CHARACTERS,
)


@dataclass(frozen=True, slots=True)
class FastGenerateRequest(VideoInputs):
    """A Fast H3 request with its image endpoints, aspect ratio, and recording interval.

    Attributes:
        aspect: Requested output aspect ratio.
        ending_image: Optional encoded ending image.

    """

    aspect: str = DEFAULT_ASPECT
    ending_image: bytes | None = None
    connection_name: ClassVar[str] = MODELS["fast-h3"].connection_name
    requires_audio: ClassVar[bool] = True

    def validate(self, settings: Settings) -> None:
        """Check Fast H3 prompt, duration, aspect ratio, and ending-image limits."""
        super(FastGenerateRequest, self).validate(settings)
        if len(self.prompt) > MAX_PROMPT_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.fastPromptLength"))
        if not MIN_CLIP_SECONDS <= self.duration_seconds <= MAX_CLIP_SECONDS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.fastDuration"))
        if self.aspect not in OPTIONS_ASPECT:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.fastAspectRatio"))
        if self.ending_image is not None and (
            type(self.ending_image) is not bytes
            or not self.ending_image
            or len(self.ending_image) > convert_mebibytes_to_bytes(settings.max_upload_megabytes)
        ):
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.endingImageUploadLimit"))

    async def begin_generation(
        self, transport: Transport, events: SessionEvents, max_capture_seconds: float
    ) -> RecordingWindow:
        """Generate and play one clip, then close its recording with trailing media."""
        audio = [
            t for t in transport.tracks if t.name == "main_audio" and t.kind == "audio" and t.direction == "recvonly"
        ]
        if len(audio) != 1:
            raise ConnectorError(ErrorCode.UNAVAILABLE, translate("main", "errors.fastAudioMissing"))
        clips = FastClipEvents(events)
        await events.command_reply("set_autoplay", {"enabled": False})
        await events.command_reply("set_flush_on_clip_end", {"enabled": False})
        await events.command_reply("set_canvas", {"aspect": self.aspect})
        state = await self._state(transport, events)
        minimum, maximum = (
            seconds(state.get("clip_seconds_min")),
            seconds(state.get("clip_seconds_max")),
        )
        if not minimum <= self.duration_seconds <= maximum:
            raise ConnectorError(
                ErrorCode.INVALID_INPUT,
                translate("main", "errors.clipDurationRange"),
            )
        clip = await self._queue_clip(transport, events, max_capture_seconds)
        await events.call("clip_build", clips.wait_ready(clip))
        start_seconds = await self._play_clip(transport, events, clips, clip)
        # Later media closes the recording fragment that contains the first clip's end.
        reply = await events.call(
            "recording_tail_queue",
            transport.send_command(
                "enqueue",
                {
                    "prompt": self.prompt,
                    "seconds": maximum,
                    "seed": self.seed,
                    "continue_from_clip_id": clip.clip_id,
                },
            ),
        )
        events.on_message(reply)
        events.check()
        tail = FastClip.read(message_payload(reply, "clip_queued"))
        if tail.seconds > maximum:
            raise ConnectorError(ErrorCode.UNAVAILABLE, translate("main", "errors.continuationLength"))
        await events.call("recording_tail_build", clips.wait_ready(tail))
        await events.command_reply("play", {"clip_id": tail.clip_id})
        return RecordingWindow(start_seconds, clip.seconds)

    async def _queue_clip(self, transport: Transport, events: SessionEvents, max_capture_seconds: float) -> FastClip:
        """Upload selected endpoint images and queue a clip within the capture limit."""
        payload: dict[str, object] = {
            "prompt": self.prompt,
            "seconds": self.duration_seconds,
            "seed": self.seed,
        }
        for name, image in (("starting_frame", self.image), ("ending_frame", self.ending_image)):
            if image is not None:
                payload[name] = await events.call(
                    "upload", transport.upload_file(image, name="input.png", mime_type="image/png")
                )
        reply = await events.call("enqueue", transport.send_command("enqueue", payload))
        events.on_message(reply)
        events.check()
        clip = FastClip.read(message_payload(reply, "clip_queued"))
        if clip.seconds > max_capture_seconds:
            raise ConnectorError(
                ErrorCode.INVALID_INPUT,
                translate("main", "errors.clipCaptureLimit"),
            )
        return clip

    async def _play_clip(
        self, transport: Transport, events: SessionEvents, clips: FastClipEvents, clip: FastClip
    ) -> float:
        """Play the chosen clip and require a precise recording interval."""
        before = await self._state(transport, events)
        start = seconds(before.get("seconds_sent"))
        if before.get("playing") is not False:
            raise ConnectorError(ErrorCode.UNAVAILABLE, translate("main", "errors.clipPlaybackOrder"))
        await events.command_reply("play", {"clip_id": clip.clip_id})
        await events.call("clip_playback", clips.finished.wait())
        end = seconds(clips.end_seconds)
        if abs(end - start - clip.seconds) > 1 / FRAME_RATE:
            raise ConnectorError(
                ErrorCode.CAPTURE,
                translate("main", "errors.clipWindowMissing"),
                diagnostic_detail=json.dumps(
                    {"start_seconds": start, "end_seconds": end, "clip_seconds": clip.seconds}
                ),
            )
        events.model_timing.update(saved_start_seconds=start, saved_duration_seconds=clip.seconds)
        return start

    async def _state(self, transport: Transport, events: SessionEvents) -> dict[str, object]:
        """Fetch the model state and process any session failure before returning it."""
        reply = await events.call("get_state", transport.send_command("get_state", {}))
        events.on_message(reply)
        events.check()
        return message_payload(reply, "state_update")
