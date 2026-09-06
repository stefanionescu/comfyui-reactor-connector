"""Build and play one Fast H3 clip with its accepted duration and native sound."""

import json
from dataclasses import dataclass, field
from typing import ClassVar

from ..config import Settings
from ..errors import ConnectorError, ErrorCode
from .events import SessionEvents
from .fast_clip import FastClip, FastClipEvents, message_data, seconds
from .inputs import VideoInputs
from .transport import Transport


@dataclass(slots=True)
class FastRecording:
    start_seconds: float = 0
    duration_seconds: float = 0
    maximum_seconds: float = 0


@dataclass(frozen=True, slots=True)
class FastGenerateRequest(VideoInputs):
    aspect: str = "16:9"
    ending_image: bytes | None = None
    model_name: ClassVar[str] = "reactor/fast-h3"
    requires_audio: ClassVar[bool] = True
    recording: FastRecording = field(default_factory=FastRecording, repr=False, compare=False)

    @property
    def recording_start_seconds(self) -> float:
        return self.recording.start_seconds

    @property
    def recording_duration_seconds(self) -> float:
        return self.recording.duration_seconds

    def validate(self, settings: Settings) -> None:
        super(FastGenerateRequest, self).validate(settings)
        if len(self.prompt) > 800:
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Use at most 800 prompt characters.")
        if not 5.167 <= self.duration_seconds <= 14.375:
            raise ConnectorError(
                ErrorCode.INVALID_INPUT, "Choose 5.167 to 14.375 seconds for Fast H3."
            )
        if self.aspect not in ("16:9", "1:1", "9:16", "4:3"):
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Choose an offered Fast H3 aspect ratio.")
        if self.ending_image is not None and (
            type(self.ending_image) is not bytes
            or not self.ending_image
            or len(self.ending_image) > settings.max_upload_megabytes * 1_048_576
        ):
            raise ConnectorError(
                ErrorCode.INVALID_INPUT, "Provide an ending image within the upload limit."
            )
        self.recording.maximum_seconds = settings.max_capture_seconds

    async def configure(self, transport: Transport, events: SessionEvents) -> None:
        audio = [
            t
            for t in transport.tracks
            if t.name == "main_audio" and t.kind == "audio" and t.direction == "recvonly"
        ]
        if len(audio) != 1:
            raise ConnectorError(
                ErrorCode.UNAVAILABLE, "This Fast H3 deployment has no audio track."
            )
        clips = FastClipEvents(events)
        await events.command("set_autoplay", {"enabled": False})
        await events.command("set_flush_on_clip_end", {"enabled": False})
        await events.command("set_canvas", {"aspect": self.aspect})
        state = await self._state(transport, events)
        minimum, maximum = (
            seconds(state.get("clip_seconds_min")),
            seconds(state.get("clip_seconds_max")),
        )
        if not minimum <= self.duration_seconds <= maximum:
            raise ConnectorError(
                ErrorCode.INVALID_INPUT,
                "The requested length is outside this deployment's clip limits.",
            )
        clip = await self._queue_clip(transport, events)
        self.recording.duration_seconds = clip.seconds
        await events.call("clip_build", clips.wait_ready(clip))
        await self._play_clip(transport, events, clips, clip)
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
        tail = FastClip.read(message_data(reply, "clip_queued"))
        if tail.seconds > maximum:
            raise ConnectorError(
                ErrorCode.UNAVAILABLE, "Fast H3 returned an invalid continuation length."
            )
        await events.call("recording_tail_build", clips.wait_ready(tail))
        await events.command("play", {"clip_id": tail.clip_id})

    async def _queue_clip(self, transport: Transport, events: SessionEvents) -> FastClip:
        data: dict[str, object] = {
            "prompt": self.prompt,
            "seconds": self.duration_seconds,
            "seed": self.seed,
        }
        for name, image in (("starting_frame", self.image), ("ending_frame", self.ending_image)):
            if image is not None:
                data[name] = await events.call(
                    "upload", transport.upload_file(image, name="input.png", mime_type="image/png")
                )
        reply = await events.call("enqueue", transport.send_command("enqueue", data))
        events.on_message(reply)
        events.check()
        clip = FastClip.read(message_data(reply, "clip_queued"))
        if clip.seconds > self.recording.maximum_seconds:
            raise ConnectorError(
                ErrorCode.INVALID_INPUT,
                "The accepted clip length exceeds the host capture limit. Choose a shorter clip.",
            )
        return clip

    async def _play_clip(
        self, transport: Transport, events: SessionEvents, clips: FastClipEvents, clip: FastClip
    ) -> None:
        before = await self._state(transport, events)
        start = seconds(before.get("seconds_sent"))
        if before.get("playing") is not False:
            raise ConnectorError(
                ErrorCode.UNAVAILABLE, "Fast H3 started playback before the clip was selected."
            )
        await events.command("play", {"clip_id": clip.clip_id})
        await events.call("clip_playback", clips.finished.wait())
        end = seconds(clips.end_seconds)
        if abs(end - start - clip.seconds) > 1 / 24:
            raise ConnectorError(
                ErrorCode.CAPTURE,
                "Fast H3 did not report a precise clip window. No partial clip will be saved.",
                diagnostic_detail=json.dumps(
                    {"start_seconds": start, "end_seconds": end, "clip_seconds": clip.seconds}
                ),
            )
        self.recording.start_seconds = start
        events.model_timing.update(saved_start_seconds=start, saved_duration_seconds=clip.seconds)

    async def _state(self, transport: Transport, events: SessionEvents) -> dict[str, object]:
        reply = await events.call("get_state", transport.send_command("get_state", {}))
        events.on_message(reply)
        events.check()
        return message_data(reply, "state_update")
