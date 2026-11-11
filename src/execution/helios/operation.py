"""Stage Helios prompt and image conditioning atomically."""

from typing import ClassVar, override
from dataclasses import asdict

from ..events import SessionEvents
from ..inputs import VideoInputOperation
from ...models import MODELS
from ..transport import SessionTransport
from ...state.session import RecordingWindow
from ...state.generation.helios import HeliosRequest


class HeliosOperation(VideoInputOperation[HeliosRequest]):
    """Stage conditioning and scheduled prompts before starting Helios.

    Attributes:
        connection_name: The provider connection of the Helios model.

    """

    connection_name: ClassVar[str] = MODELS['helios'].connection_name

    @override
    async def begin_generation(self, transport: SessionTransport, events: SessionEvents) -> RecordingWindow:
        """Set the initial image or prompt, schedule later prompts, and start generation.

        Args:
            transport: The connected transport that uploads the image.
            events: The session events that send each command.

        Returns:
            The recording interval for the requested duration.

        """
        inputs = self.inputs
        await events.command_reply('set_seed', {'seed': inputs.seed})
        if inputs.image is None:
            await events.command_reply('set_prompt', {'prompt': inputs.prompt})
        else:
            reference = await transport.upload_file(inputs.image, name='input.png', mime_type='image/png')
            await events.command_reply('set_conditioning', {'prompt': inputs.prompt, 'image': reference})
        for prompt in inputs.prompts:
            await events.command_reply('schedule_prompt', asdict(prompt))
        await events.command_reply('start', {})
        return RecordingWindow(0, inputs.duration_seconds)
