"""Chain a chosen number of Fast H3 clips in one session and save their sound."""

from dataclasses import dataclass

from ..config import Settings
from ..errors import ConnectorError, ErrorCode
from .events import SessionEvents
from .fast import FastGenerateRequest
from .fast_clip import FastClip, FastClipEvents, message_data, seconds
from .inputs import VideoInputs
from .transport import Transport


@dataclass(frozen=True, slots=True)
class FastContinueRequest(FastGenerateRequest):
    clip_seconds: float = 6
    clip_count: int = 3
    later_prompts: tuple[str, ...] = ()

    def validate(self, settings: Settings) -> None:
        VideoInputs.validate(self, settings)
        if type(self.clip_count) is not int or not 2 <= self.clip_count <= 8:
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Choose 2 to 8 clips.")
        if type(self.clip_seconds) not in (int, float) or not 5.167 <= self.clip_seconds <= 14.375:
            raise ConnectorError(
                ErrorCode.INVALID_INPUT, "Choose 5.167 to 14.375 seconds per clip."
            )
        if self.aspect not in ("16:9", "1:1", "9:16", "4:3"):
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Choose an offered aspect ratio.")
        prompts = (self.prompt, *self.later_prompts)
        if len(self.later_prompts) > self.clip_count - 1 or any(
            type(prompt) is not str or not prompt.strip() or len(prompt) > 800 for prompt in prompts
        ):
            raise ConnectorError(
                ErrorCode.INVALID_INPUT,
                "Use at most 800 characters per prompt and one later prompt per remaining clip.",
            )
        self.recording.maximum_seconds = settings.max_capture_seconds

    async def configure(self, transport: Transport, events: SessionEvents) -> None:
        if not any(
            track.name == "main_audio" and track.kind == "audio" and track.direction == "recvonly"
            for track in transport.tracks
        ):
            raise ConnectorError(
                ErrorCode.UNAVAILABLE, "This Fast H3 deployment has no audio track."
            )
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
                "This deployment does not support the requested clip length.",
            )
        current = await self._enqueue(events, None, 0)
        await events.call("clip_build", clips.wait_ready(current))
        state = await self._state(transport, events)
        if state.get("playing") is not False:
            raise ConnectorError(
                ErrorCode.UNAVAILABLE, "Fast H3 started playback before the sequence was ready."
            )
        self.recording.start_seconds = seconds(state.get("seconds_sent"))
        await events.command("set_autoplay", {"enabled": True})
        # Queue one continuation ahead. Each clip opens from the previous clip's last frame.
        for index in range(1, self.clip_count):
            following = await self._enqueue(events, current, index)
            await events.call("clip_playback", clips.wait_finished(current))
            current = following
        end = await events.call("clip_playback", clips.wait_finished(current))
        await events.command("set_autoplay", {"enabled": False})
        duration = end - self.recording.start_seconds
        if not 0 < duration <= self.recording.maximum_seconds:
            raise ConnectorError(
                ErrorCode.CAPTURE,
                (
                    "The sequence exceeded the video duration limit. Choose fewer clips or "
                    "a longer limit."
                ),
            )
        self.recording.duration_seconds = duration
        events.model_timing.update(
            saved_start_seconds=self.recording.start_seconds, saved_duration_seconds=duration
        )
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
        prompt = (
            self.later_prompts[index - 1] if 0 < index <= len(self.later_prompts) else self.prompt
        )
        data: dict[str, object] = {
            "prompt": prompt,
            "seconds": duration or self.clip_seconds,
            "seed": (self.seed + index) % 2**32,
        }
        if previous is not None:
            data["continue_from_clip_id"] = previous.clip_id
        elif self.image is not None:
            data["starting_frame"] = await events.call(
                "upload",
                events.transport.upload_file(self.image, name="input.png", mime_type="image/png"),
            )
        reply = await events.command_reply("enqueue", data)
        clip = FastClip.read(message_data(reply, "clip_queued"))
        if duration is None and clip.seconds * self.clip_count > self.recording.maximum_seconds:
            raise ConnectorError(
                ErrorCode.INVALID_INPUT,
                "The accepted clip lengths exceed the video duration limit. Choose fewer clips.",
            )
        return clip
