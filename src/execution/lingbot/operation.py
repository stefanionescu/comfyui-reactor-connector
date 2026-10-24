"""Convert camera directions into commands supported by LingBot."""

import math
from typing import ClassVar, override

from ..events import SessionEvents
from ..inputs import VideoInputOperation
from ...errors import ErrorCode, ConnectorError
from ...models import MODELS
from ..transport import SessionTransport
from ...state.session import RecordingWindow
from ...state.settings import Settings
from ...config.messages.live import CAMERA_DIRECTION
from ...config.messages.media import STARTING_IMAGE_REQUIRED
from ...config.messages.inputs import ROTATION_SPEED, LATERAL_DIRECTION, WORLD_PROMPT_LENGTH
from ...config.generation.world import (
    CAMERA_AXES,
    WORLD_FRAME_RATE,
    MAX_ROTATION_SPEED,
    MIN_ROTATION_SPEED,
    MAX_WORLD_PROMPT_CHARACTERS,
)
from ...state.generation.lingbot import LingBotRequest, LingBotWorldRequest


class LingBotOperation[Request: LingBotRequest](VideoInputOperation[Request]):
    """Hold the requested camera controls while generating from an image."""

    connection_name: ClassVar[str] = MODELS['lingbot'].connection_name
    movement_values: ClassVar[tuple[str, ...]] = CAMERA_AXES['movement']

    def axes(self) -> tuple[tuple[str, str], ...]:
        """Map camera directions to the command names of the selected LingBot version."""
        inputs = self.inputs
        if isinstance(inputs, LingBotWorldRequest):
            return (
                ('move_longitudinal', inputs.movement),
                ('move_lateral', inputs.lateral),
                ('look_horizontal', inputs.look_horizontal),
                ('look_vertical', inputs.look_vertical),
            )
        return (
            ('movement', inputs.movement),
            ('look_horizontal', inputs.look_horizontal),
            ('look_vertical', inputs.look_vertical),
        )

    @override
    def validate(self, settings: Settings) -> None:
        """Require an image, supported directions, and a finite camera rotation speed."""
        super().validate(settings)
        inputs = self.inputs
        if inputs.image is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, STARTING_IMAGE_REQUIRED)
        if len(inputs.prompt) > MAX_WORLD_PROMPT_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, WORLD_PROMPT_LENGTH)
        allowed = (
            (inputs.movement, self.movement_values),
            (inputs.look_horizontal, CAMERA_AXES['look_horizontal']),
            (inputs.look_vertical, CAMERA_AXES['look_vertical']),
        )
        if any(value not in choices for value, choices in allowed):
            raise ConnectorError(ErrorCode.INVALID_INPUT, CAMERA_DIRECTION)
        speed = inputs.rotation_speed_deg
        if not math.isfinite(speed) or not MIN_ROTATION_SPEED <= speed <= MAX_ROTATION_SPEED:
            raise ConnectorError(ErrorCode.INVALID_INPUT, ROTATION_SPEED)

    @override
    async def begin_generation(self, transport: SessionTransport, events: SessionEvents) -> RecordingWindow:
        """Upload the starting image, set camera controls, and start the scene."""
        inputs = self.inputs
        if inputs.image is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, STARTING_IMAGE_REQUIRED)
        await events.command_reply('set_seed', {'seed': inputs.seed})
        reference = await transport.upload_file(inputs.image, name='input.png', mime_type='image/png')
        await events.command_reply('set_image', {'image': reference})
        await events.command_reply('set_prompt', {'prompt': inputs.prompt})
        await events.command_reply('set_rotation_speed_deg', {'rotation_speed_deg': inputs.rotation_speed_deg})
        for axis, value in self.axes():
            await events.command_reply(f'set_{axis}', {axis: value})
        await events.command_reply('start', {})
        return RecordingWindow(0, inputs.duration_seconds)

    async def release(self, transport: SessionTransport) -> None:
        """Release held axes before disconnect; disconnect still runs if release fails."""
        client = transport.client
        if client is not None and client.status == 'ready':
            for axis, _ in self.axes():
                await transport.get_client().send_command(f'set_{axis}', {axis: 'idle'})


class LingBotWorldOperation(LingBotOperation[LingBotWorldRequest]):
    """Hold longitudinal and lateral camera controls independently for World 2."""

    connection_name: ClassVar[str] = MODELS['lingbot-world-2'].connection_name
    default_fps: ClassVar[int] = WORLD_FRAME_RATE
    movement_values: ClassVar[tuple[str, ...]] = CAMERA_AXES['move_longitudinal']

    @override
    def validate(self, settings: Settings) -> None:
        """Check the shared camera settings and World 2 lateral direction."""
        super().validate(settings)
        if self.inputs.lateral not in CAMERA_AXES['move_lateral']:
            raise ConnectorError(ErrorCode.INVALID_INPUT, LATERAL_DIRECTION)
