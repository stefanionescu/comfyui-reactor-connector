"""Build and play one Fast H3 clip with its accepted duration and native sound."""

from typing import ClassVar, override

from .clip import FastClipEvents, seconds, read_clip, message_payload
from ..events import SessionEvents
from ..inputs import VideoInputOperation
from ...errors import ErrorCode, ConnectorError
from ...models import MODELS
from ..transport import SessionTransport
from ...config.nodes import MAX_DURATION_SECONDS
from ...state.session import RecordingWindow
from ...state.settings import Settings
from ...config.settings import BYTES_PER_MEBIBYTE
from ...config.messages.media import ENDING_IMAGE_UPLOAD_LIMIT
from ...state.generation.fast import FastClip, FastGenerateRequest
from ...config.generation.fast import (
    FRAME_RATE,
    OPTIONS_ASPECT,
    MAX_CLIP_SECONDS,
    MIN_CLIP_SECONDS,
    MAX_PROMPT_CHARACTERS,
)
from ...config.messages.inputs import (
    FAST_DURATION,
    FAST_ASPECT_RATIO,
    CLIP_CAPTURE_LIMIT,
    FAST_AUDIO_MISSING,
    FAST_PROMPT_LENGTH,
    CLIP_DURATION_RANGE,
    CLIP_PLAYBACK_ORDER,
    CLIP_WINDOW_MISSING,
    CONTINUATION_LENGTH,
)


class FastGenerateOperation[Request: FastGenerateRequest](VideoInputOperation[Request]):
    """Build and play a clip with the requested image endpoints and aspect ratio."""

    connection_name: ClassVar[str] = MODELS['fast-h3'].connection_name
    requires_audio: ClassVar[bool] = True

    @override
    def validate(self, settings: Settings) -> None:
        """Check the shared capture limits, then the Fast H3 prompt, duration, aspect ratio, and ending image."""
        super().validate(settings)
        if len(self.inputs.prompt) > MAX_PROMPT_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, FAST_PROMPT_LENGTH)
        if not MIN_CLIP_SECONDS <= self.inputs.duration_seconds <= MAX_CLIP_SECONDS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, FAST_DURATION)
        if self.inputs.aspect not in OPTIONS_ASPECT:
            raise ConnectorError(ErrorCode.INVALID_INPUT, FAST_ASPECT_RATIO)
        if self.inputs.ending_image is not None and (
            not self.inputs.ending_image
            or len(self.inputs.ending_image) > settings.max_upload_megabytes * BYTES_PER_MEBIBYTE
        ):
            raise ConnectorError(ErrorCode.INVALID_INPUT, ENDING_IMAGE_UPLOAD_LIMIT)

    @override
    async def begin_generation(self, transport: SessionTransport, events: SessionEvents) -> RecordingWindow:
        """Generate and play one clip, then close its recording with trailing media."""
        audio = [
            t
            for t in transport.get_client().tracks
            if t.name == 'main_audio' and t.kind == 'audio' and t.direction == 'recvonly'
        ]
        if len(audio) != 1:
            raise ConnectorError(ErrorCode.UNAVAILABLE, FAST_AUDIO_MISSING)
        clips = FastClipEvents(events)
        minimum, maximum = await self._read_clip_range(transport, events)
        if not minimum <= self.inputs.duration_seconds <= maximum:
            raise ConnectorError(
                ErrorCode.INVALID_INPUT,
                CLIP_DURATION_RANGE,
            )
        clip = await self._queue_clip(transport, events)
        await events.call('clip_build', clips.wait_ready(clip))
        start_seconds = await self._play_clip(transport, events, clips, clip)
        # Later media closes the recording fragment that contains the first clip's end.
        reply = await events.call(
            'recording_tail_queue',
            transport.get_client().send_command(
                'enqueue',
                {
                    'prompt': self.inputs.prompt,
                    'seconds': maximum,
                    'seed': self.inputs.seed,
                    'continue_from_clip_id': clip.clip_id,
                },
            ),
        )
        events.accept_reply(reply)
        tail = read_clip(message_payload(reply, 'clip_queued'))
        if tail.seconds > maximum:
            raise ConnectorError(ErrorCode.UNAVAILABLE, CONTINUATION_LENGTH)
        await events.call('recording_tail_build', clips.wait_ready(tail))
        await events.command_reply('play', {'clip_id': tail.clip_id})
        return RecordingWindow(start_seconds, clip.seconds)

    async def _queue_clip(self, transport: SessionTransport, events: SessionEvents) -> FastClip:
        """Upload selected endpoint images and queue a clip within the video duration limit."""
        payload: dict[str, object] = {
            'prompt': self.inputs.prompt,
            'seconds': self.inputs.duration_seconds,
            'seed': self.inputs.seed,
        }
        for name, image in (('starting_frame', self.inputs.image), ('ending_frame', self.inputs.ending_image)):
            if image is not None:
                payload[name] = await events.call(
                    'upload', transport.upload_file(image, name='input.png', mime_type='image/png')
                )
        reply = await events.call('enqueue', transport.get_client().send_command('enqueue', payload))
        events.accept_reply(reply)
        clip = read_clip(message_payload(reply, 'clip_queued'))
        if clip.seconds > MAX_DURATION_SECONDS:
            raise ConnectorError(
                ErrorCode.INVALID_INPUT,
                CLIP_CAPTURE_LIMIT,
            )
        return clip

    async def _play_clip(
        self, transport: SessionTransport, events: SessionEvents, clips: FastClipEvents, clip: FastClip
    ) -> float:
        """Play the chosen clip and require a precise recording interval."""
        before = await self._state(transport, events)
        start = seconds(before.get('seconds_sent'))
        if before.get('playing') is not False:
            raise ConnectorError(ErrorCode.UNAVAILABLE, CLIP_PLAYBACK_ORDER)
        await events.command_reply('play', {'clip_id': clip.clip_id})
        await events.call('clip_playback', clips.finished.wait())
        end = seconds(clips.end_seconds)
        if abs(end - start - clip.seconds) > 1 / FRAME_RATE:
            raise ConnectorError(ErrorCode.CAPTURE, CLIP_WINDOW_MISSING)
        return start

    async def _read_clip_range(self, transport: SessionTransport, events: SessionEvents) -> tuple[float, float]:
        """Stop autoplay and end-of-clip flushing, set the canvas, and read the clip lengths that the model accepts."""
        await events.command_reply('set_autoplay', {'enabled': False})
        await events.command_reply('set_flush_on_clip_end', {'enabled': False})
        await events.command_reply('set_canvas', {'aspect': self.inputs.aspect})
        state = await self._state(transport, events)
        return seconds(state.get('clip_seconds_min')), seconds(state.get('clip_seconds_max'))

    async def _state(self, transport: SessionTransport, events: SessionEvents) -> dict[str, object]:
        """Fetch the model state and process any session failure before returning it."""
        reply = await events.call('get_state', transport.get_client().send_command('get_state', {}))
        events.accept_reply(reply)
        return message_payload(reply, 'state_update')
