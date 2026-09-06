"""Stage Helios prompt and image conditioning atomically."""

import json
from dataclasses import dataclass
from typing import ClassVar

from ..config import Settings
from .events import SessionEvents
from .inputs import VideoInputs
from .prompt_sequence import ScheduledPrompt, parse_sequence
from .transport import Transport


@dataclass(frozen=True, slots=True)
class HeliosRequest(VideoInputs):
    """Generate a Helios video of the requested length from a prompt and optional image."""

    prompts: tuple[ScheduledPrompt, ...] = ()
    model_name: ClassVar[str] = "reactor/helios"

    def validate(self, settings: Settings) -> None:
        VideoInputs.validate(self, settings)
        parse_sequence(json.dumps([prompt.to_dict() for prompt in self.prompts]))

    async def configure(self, transport: Transport, events: SessionEvents) -> None:
        await events.command("set_seed", {"seed": self.seed})
        if self.image is None:
            await events.command("set_prompt", {"prompt": self.prompt})
        else:
            reference = await transport.upload_file(
                self.image, name="input.png", mime_type="image/png"
            )
            await events.command("set_conditioning", {"prompt": self.prompt, "image": reference})
        for prompt in self.prompts:
            await events.command("schedule_prompt", prompt.to_dict())
        await events.command("start", {})
