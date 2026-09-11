"""Stage Helios prompt and image conditioning atomically."""

import json
from typing import ClassVar
from ..inputs import VideoInputs
from ..transport import Transport
from dataclasses import dataclass
from ..events import SessionEvents
from ...model_registry import MODELS
from ..operation import RecordingWindow
from ...settings.settings import Settings
from .prompts import parse_sequence, ScheduledPrompt


@dataclass(frozen=True, slots=True)
class HeliosRequest(VideoInputs):
    """Generate a Helios video of the requested length from a prompt and optional image.

    Attributes:
        prompts: Prompt changes scheduled during generation.

    """

    prompts: tuple[ScheduledPrompt, ...] = ()
    model_name: ClassVar[str] = MODELS["helios"].connection_name

    def validate(self, settings: Settings) -> None:
        """Check the capture inputs and every scheduled prompt."""
        VideoInputs.validate(self, settings)
        parse_sequence(json.dumps([prompt.to_dict() for prompt in self.prompts]))

    async def configure(
        self, transport: Transport, events: SessionEvents, max_capture_seconds: float
    ) -> RecordingWindow:
        """Set the initial image or prompt, schedule later prompts, and start generation."""
        del max_capture_seconds
        await events.command_reply("set_seed", {"seed": self.seed})
        if self.image is None:
            await events.command_reply("set_prompt", {"prompt": self.prompt})
        else:
            reference = await transport.upload_file(self.image, name="input.png", mime_type="image/png")
            await events.command_reply("set_conditioning", {"prompt": self.prompt, "image": reference})
        for prompt in self.prompts:
            await events.command_reply("schedule_prompt", prompt.to_dict())
        await events.command_reply("start", {})
        return RecordingWindow(0, self.duration_seconds)
