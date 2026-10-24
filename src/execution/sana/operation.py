"""Prepare the source video before asking SANA to edit it."""

from typing import ClassVar, cast, override
import asyncio

from ..events import SessionEvents
from ..inputs import VideoInputOperation, validate_capture_inputs
from ...errors import ErrorCode, ConnectorError
from ...models import MODELS
from .contract import source_mode
from ..transport import SessionTransport
from ...media.webcam import WebcamFrames
from ...state.session import RecordingWindow
from ...state.settings import Settings
from ...media.video.publish import VideoPublication
from ...config.messages.media import SOURCE_VIDEO_REQUIRED
from ...state.generation.sana import SanaRequest
from ...config.messages.inputs import ANCHOR_INTERVAL, SANA_PROMPT_LENGTH, SANA_WEBCAM_UNSUPPORTED
from ...config.generation.video import MAX_ANCHOR_INTERVAL, MIN_ANCHOR_INTERVAL
from ...config.generation.session import MAX_PROMPT_CHARACTERS


class SanaOperation(VideoInputOperation[SanaRequest]):
    """Own source publication and model commands for one SANA edit.

    Attributes:
        webcam: Optional browser camera that publishes source frames.
        publication: Owned source video publisher.

    """

    connection_name: ClassVar[str] = MODELS['sana-streaming'].connection_name

    def __init__(self, inputs: SanaRequest, *, webcam: WebcamFrames | None = None) -> None:
        """Bind source inputs, the optional webcam, and their publication owner."""
        super().__init__(inputs)
        self.webcam = webcam
        self.publication = VideoPublication()

    @override
    def validate(self, settings: Settings) -> None:
        """Check capture limits, source availability, prompt size, and anchor interval."""
        inputs = self.inputs
        validate_capture_inputs(inputs.duration_seconds, inputs.seed, settings)
        if len(inputs.prompt) > MAX_PROMPT_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, SANA_PROMPT_LENGTH)
        if inputs.video is None and self.webcam is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, SOURCE_VIDEO_REQUIRED)
        if not MIN_ANCHOR_INTERVAL <= inputs.anchor_interval <= MAX_ANCHOR_INTERVAL:
            raise ConnectorError(ErrorCode.INVALID_INPUT, ANCHOR_INTERVAL)

    @override
    async def begin_generation(self, transport: SessionTransport, events: SessionEvents) -> RecordingWindow:
        """Prepare the source using the declared model contract and start video editing."""
        inputs = self.inputs
        if inputs.video is None and self.webcam is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, SOURCE_VIDEO_REQUIRED)
        schema = await events.call('schema', transport.get_client().request_schema())
        mode = source_mode(schema, transport)
        if self.webcam is not None and mode != 'camera':
            raise ConnectorError(ErrorCode.UNAVAILABLE, SANA_WEBCAM_UNSUPPORTED)
        if mode == 'file':
            await self._accept_file(transport, events)
        await events.command_reply('set_seed', {'seed': inputs.seed})
        if inputs.prompt.strip():
            await events.command_reply('set_prompt', {'prompt': inputs.prompt})
        await events.command_reply('set_anchor_interval', {'chunks': inputs.anchor_interval})
        if mode == 'file':
            await events.command_reply('set_mode', {'mode': 'file'})
        else:
            track = await events.call('publish_camera', transport.get_client().publish_track('camera'))
            if self.webcam is not None:
                self.webcam.task = asyncio.create_task(self.webcam.publish(track, events.on_error))
            elif inputs.video is not None:
                await self.publication.begin(inputs.video, track, events.on_error)
        await events.command_reply('start', {})
        self.publication.started.set()
        return RecordingWindow(0, inputs.duration_seconds)

    async def release(self, transport: SessionTransport) -> None:
        """Stop source publication and close any webcam input."""
        del transport
        await self.publication.close()
        if self.webcam is not None:
            await self.webcam.close()

    async def _accept_file(self, transport: SessionTransport, events: SessionEvents) -> None:
        """Upload the source and wait for model acceptance, then remove the temporary listener."""
        if self.inputs.video is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, SOURCE_VIDEO_REQUIRED)
        accepted = asyncio.Event()

        def observe(message: object) -> None:
            """Signal only a model state that confirms the model accepted the uploaded video."""
            if not isinstance(message, dict):
                return
            document = cast('dict[str, object]', message)
            payload = document.get('data')
            if (
                document.get('type') == 'state'
                and isinstance(payload, dict)
                and cast('dict[str, object]', payload).get('has_video') is True
            ):
                accepted.set()

        transport.on('message', observe)
        try:
            reference = await events.call(
                'upload', transport.upload_file(self.inputs.video, name='input.mp4', mime_type='video/mp4')
            )
            await events.command_reply('set_video', {'video': reference})
            await accepted.wait()
        finally:
            transport.off('message', observe)
