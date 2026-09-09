"""Stage Helios prompt and image conditioning atomically."""

import json
from typing import ClassVar
from ..inputs import VideoInputs
from ..transport import Transport
from dataclasses import dataclass
from ..events import SessionEvents
from ...settings.settings import Settings
from ....config.models.identities import IDENTITIES
from .prompts import parse_sequence, ScheduledPrompt


@dataclass(frozen=True, slots=True)
class HeliosRequest(VideoInputs):
    """Generate a Helios video of the requested length from a prompt and optional image."""

    prompts: tuple[ScheduledPrompt, ...] = ()
    model_name: ClassVar[str] = IDENTITIES["helios"][1]

    def validate(self, settings: Settings) -> None:
        """Check the capture inputs and every scheduled prompt."""
        VideoInputs.validate(self, settings)
        parse_sequence(json.dumps([prompt.to_dict() for prompt in self.prompts]))

    async def configure(self, transport: Transport, events: SessionEvents) -> None:
        """Set the initial image or prompt, schedule later prompts, and start generation."""
        await events.command("set_seed", {"seed": self.seed})
        if self.image is None:
            await events.command("set_prompt", {"prompt": self.prompt})
        else:
            reference = await transport.upload_file(self.image, name="input.png", mime_type="image/png")
            await events.command("set_conditioning", {"prompt": self.prompt, "image": reference})
        for prompt in self.prompts:
            await events.command("schedule_prompt", prompt.to_dict())
        await events.command("start", {})
