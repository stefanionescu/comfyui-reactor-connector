"""Stage Helios prompt and image conditioning atomically."""

import json
from typing import ClassVar
from ...models import MODELS
from ..transport import Transport
from ..events import SessionEvents
from .prompts import parse_sequence
from ...state.settings import Settings
from ..inputs import VideoInputOperation
from ...state.session import RecordingWindow
from ...state.generation.helios import HeliosRequest


class HeliosOperation(VideoInputOperation[HeliosRequest]):
    """Stage conditioning and scheduled prompts before starting Helios."""

    connection_name: ClassVar[str] = MODELS["helios"].connection_name

    def validate(self, settings: Settings) -> None:
        """Check the capture inputs and every scheduled prompt."""
        super().validate(settings)
        parse_sequence(json.dumps([prompt.to_dict() for prompt in self.inputs.prompts]))

    async def begin_generation(
        self, transport: Transport, events: SessionEvents, max_capture_seconds: float
    ) -> RecordingWindow:
        """Set the initial image or prompt, schedule later prompts, and start generation."""
        del max_capture_seconds
        inputs = self.inputs
        await events.command_reply("set_seed", {"seed": inputs.seed})
        if inputs.image is None:
            await events.command_reply("set_prompt", {"prompt": inputs.prompt})
        else:
            reference = await transport.upload_file(inputs.image, name="input.png", mime_type="image/png")
            await events.command_reply("set_conditioning", {"prompt": inputs.prompt, "image": reference})
        for prompt in inputs.prompts:
            await events.command_reply("schedule_prompt", prompt.to_dict())
        await events.command_reply("start", {})
        return RecordingWindow(0, inputs.duration_seconds)


__all__ = ["HeliosOperation"]
