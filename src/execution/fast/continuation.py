"""Chain a chosen number of Fast H3 clips in one session and save their sound."""

from typing import override

from .clip import FastClipEvents, seconds, read_clip, message_payload
from ..events import SessionEvents
from ..inputs import VideoInputOperation
from ...errors import ErrorCode, ConnectorError
from .generate import FastGenerateOperation
from ..transport import SessionTransport
from ...config.nodes import MAX_SEED, MAX_DURATION_SECONDS
from ...state.session import RecordingWindow
from ...state.settings import Settings
from ...state.generation.fast import FastClip, FastContinueRequest
from ...config.generation.fast import (
    MAX_CLIP_COUNT,
    MIN_CLIP_COUNT,
    OPTIONS_ASPECT,
    MAX_CLIP_SECONDS,
    MIN_CLIP_SECONDS,
    MAX_PROMPT_CHARACTERS,
)
from ...config.messages.inputs import (
    CLIP_COUNT,
    ASPECT_RATIO,
    FAST_AUDIO_MISSING,
    CONTINUATION_PROMPTS,
    SEQUENCE_CAPTURE_LIMIT,
    ACCEPTED_SEQUENCE_LIMIT,
    CONTINUED_CLIP_DURATION,
    SEQUENCE_PLAYBACK_ORDER,
    CLIP_DURATION_UNSUPPORTED,
)


class FastContinueOperation(FastGenerateOperation[FastContinueRequest]):
    """Chain the requested clips while preserving their accepted media intervals."""

    @override
    def validate(self, settings: Settings) -> None:
        """Check the shared capture limits, then clip count, clip length, aspect ratio, and prompts for the chain."""
        VideoInputOperation[FastContinueRequest].validate(self, settings)
        if not MIN_CLIP_COUNT <= self.inputs.clip_count <= MAX_CLIP_COUNT:
            raise ConnectorError(ErrorCode.INVALID_INPUT, CLIP_COUNT)
        if not MIN_CLIP_SECONDS <= self.inputs.clip_seconds <= MAX_CLIP_SECONDS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, CONTINUED_CLIP_DURATION)
        if self.inputs.aspect not in OPTIONS_ASPECT:
            raise ConnectorError(ErrorCode.INVALID_INPUT, ASPECT_RATIO)
        prompts = (self.inputs.prompt, *self.inputs.later_prompts)
        if len(self.inputs.later_prompts) > self.inputs.clip_count - 1 or any(
            not prompt.strip() or len(prompt) > MAX_PROMPT_CHARACTERS for prompt in prompts
        ):
            raise ConnectorError(
                ErrorCode.INVALID_INPUT,
                CONTINUATION_PROMPTS,
            )

    @override
    async def begin_generation(self, transport: SessionTransport, events: SessionEvents) -> RecordingWindow:
        """Play linked clips and enough trailing media to finish the saved recording."""
        if not any(
            track.name == 'main_audio' and track.kind == 'audio' and track.direction == 'recvonly'
            for track in transport.get_client().tracks
        ):
            raise ConnectorError(ErrorCode.UNAVAILABLE, FAST_AUDIO_MISSING)
        clips = FastClipEvents(events, limit=self.inputs.clip_count + 1)
        minimum, maximum = await self._read_clip_range(transport, events)
        if not minimum <= self.inputs.clip_seconds <= maximum:
            raise ConnectorError(
                ErrorCode.INVALID_INPUT,
                CLIP_DURATION_UNSUPPORTED,
            )
        current = await self._enqueue(events, None, 0)
        # The model may accept a clip length other than the requested one; the chain must still fit the duration limit.
        if current.seconds * self.inputs.clip_count > MAX_DURATION_SECONDS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, ACCEPTED_SEQUENCE_LIMIT)
        await events.call('clip_build', clips.wait_ready(current))
        start_seconds = await self._read_playback_start(transport, events)
        await events.command_reply('set_autoplay', {'enabled': True})
        # Queue one continuation ahead. Each clip opens from the previous clip's last frame.
        for index in range(1, self.inputs.clip_count):
            following = await self._enqueue(events, current, index)
            if following.seconds * self.inputs.clip_count > MAX_DURATION_SECONDS:
                raise ConnectorError(ErrorCode.INVALID_INPUT, ACCEPTED_SEQUENCE_LIMIT)
            await events.call('clip_playback', clips.wait_finished(current))
            current = following
        duration = await events.call('clip_playback', clips.wait_finished(current)) - start_seconds
        await events.command_reply('set_autoplay', {'enabled': False})
        if not 0 < duration <= MAX_DURATION_SECONDS:
            raise ConnectorError(
                ErrorCode.CAPTURE,
                (SEQUENCE_CAPTURE_LIMIT),
            )
        # The recorder needs later media to close its final fragment.
        tail = await self._enqueue(events, current, self.inputs.clip_count, duration=maximum)
        await events.call('recording_tail_build', clips.wait_ready(tail))
        await events.command_reply('play', {'clip_id': tail.clip_id})
        return RecordingWindow(start_seconds, duration)

    async def _read_playback_start(self, transport: SessionTransport, events: SessionEvents) -> float:
        """Read the recording position only while automatic playback stays stopped."""
        state = await self._state(transport, events)
        if state.get('playing') is not False:
            raise ConnectorError(ErrorCode.UNAVAILABLE, SEQUENCE_PLAYBACK_ORDER)
        return seconds(state.get('seconds_sent'))

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
            self.inputs.later_prompts[index - 1] if 0 < index <= len(self.inputs.later_prompts) else self.inputs.prompt
        )
        payload: dict[str, object] = {
            'prompt': prompt,
            'seconds': duration or self.inputs.clip_seconds,
            'seed': (self.inputs.seed + index) % (MAX_SEED + 1),
        }
        if previous is not None:
            payload['continue_from_clip_id'] = previous.clip_id
        elif self.inputs.image is not None:
            payload['starting_frame'] = await events.call(
                'upload',
                events.transport.upload_file(self.inputs.image, name='input.png', mime_type='image/png'),
            )
        reply = await events.command_reply('enqueue', payload)
        return read_clip(message_payload(reply, 'clip_queued'))
