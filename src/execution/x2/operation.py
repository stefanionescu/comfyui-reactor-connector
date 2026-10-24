"""Publish a local source to X2 after its editing controls are ready."""

from typing import ClassVar, override
import asyncio

from ..events import SessionEvents
from ..inputs import VideoInputOperation
from ...errors import ErrorCode, ConnectorError
from ...models import MODELS
from ..transport import SessionTransport
from ...config.nodes import MAX_POINTER_POSITION, MIN_POINTER_POSITION
from ...media.webcam import WebcamFrames
from ...serialization import mapping_value, validate_json
from ...state.session import RecordingWindow
from ...state.settings import Settings
from ...media.video.publish import VideoPublication
from ...state.generation.x2 import X2Request
from ...config.messages.live import POINTER_COORDINATES
from ...config.messages.media import SOURCE_VIDEO_REQUIRED
from ...config.messages.inputs import XMAX_UNSUPPORTED, XMAX_PROMPT_LENGTH
from ...config.generation.video import MAX_EDIT_PROMPT_CHARACTERS


class X2Operation(VideoInputOperation[X2Request]):
    """Own source publication and pointer controls for one edit.

    Attributes:
        webcam: Optional browser camera that publishes source frames.
        publication: Owned source video publisher.

    """

    connection_name: ClassVar[str] = MODELS['x2'].connection_name

    def __init__(self, inputs: X2Request, *, webcam: WebcamFrames | None = None) -> None:
        """Bind edit values, the optional webcam, and their source publication owner."""
        super().__init__(inputs)
        self.webcam = webcam
        self.publication = VideoPublication()

    @override
    def validate(self, settings: Settings) -> None:
        """Check the source, prompt, backlog option, and normalized pointer coordinates."""
        super().validate(settings)
        inputs = self.inputs
        if len(inputs.prompt) > MAX_EDIT_PROMPT_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, XMAX_PROMPT_LENGTH)
        if inputs.video is None and self.webcam is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, SOURCE_VIDEO_REQUIRED)
        if any(
            not MIN_POINTER_POSITION <= value <= MAX_POINTER_POSITION for value in (inputs.pointer_x, inputs.pointer_y)
        ):
            raise ConnectorError(ErrorCode.INVALID_INPUT, POINTER_COORDINATES)

    @override
    async def begin_generation(self, transport: SessionTransport, events: SessionEvents) -> RecordingWindow:
        """Verify X2 commands, set the reference and pointer, and publish the source video."""
        inputs = self.inputs
        if inputs.video is None and self.webcam is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, SOURCE_VIDEO_REQUIRED)
        schema = await events.call('schema', transport.get_client().request_schema())
        _validate_contract(schema, transport)
        if inputs.image is not None:
            reference = await events.call(
                'upload', transport.upload_file(inputs.image, name='input.png', mime_type='image/png')
            )
            await events.command_reply('set_reference_image', {'reference_image': reference})
        await events.command_reply('set_keep_backlog', {'keep_backlog': inputs.keep_backlog})
        await events.command_reply(
            'set_pointer',
            {'x': inputs.pointer_x, 'y': inputs.pointer_y, 'active': inputs.pointer_active},
        )
        await events.command_reply('set_prompt', {'prompt': inputs.prompt})
        track = await events.call('publish_source', transport.get_client().publish_track('source'))
        if self.webcam is not None:
            self.webcam.task = asyncio.create_task(self.webcam.publish(track, events.on_error))
        elif inputs.video is not None:
            await self.publication.begin(inputs.video, track, events.on_error)
        self.publication.started.set()
        return RecordingWindow(0, inputs.duration_seconds)

    async def release(self, transport: SessionTransport) -> None:
        """Stop source publication and release the active pointer while connected."""
        await self.publication.close()
        if self.webcam is not None:
            await self.webcam.close()
        client = transport.client
        if self.inputs.pointer_active and client is not None and client.status == 'ready':
            await transport.get_client().send_command('set_pointer_active', {'pointer_active': False})


def _validate_contract(schema: object, transport: SessionTransport) -> None:
    """Require the X2 edit commands and one send-only source video track."""
    document = mapping_value(validate_json(schema))
    paths = mapping_value(document.get('paths'))
    required = {
        'set_prompt',
        'set_reference_image',
        'set_keep_backlog',
        'set_pointer',
        'set_pointer_active',
    }
    commands = {
        name
        for name in required
        if mapping_value(mapping_value(paths.get(f'/events/{name}')).get('post')).get('operationId') == name
    }
    sources = [
        track
        for track in transport.get_client().tracks
        if track.name == 'source' and track.kind == 'video' and track.direction == 'sendonly'
    ]
    if commands != required or len(sources) != 1:
        raise ConnectorError(ErrorCode.UNAVAILABLE, XMAX_UNSUPPORTED)
