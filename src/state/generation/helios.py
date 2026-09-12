"""Helios request and scheduled prompt records."""

from .inputs import VideoInputs
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ScheduledPrompt:
    """A later prompt on Helios's chunk clock.

    Attributes:
        chunk: Chunk at which the prompt changes.
        prompt: Scene text for subsequent generation.

    """

    chunk: int
    prompt: str

    def to_dict(self) -> dict[str, object]:
        """Encode the scheduled prompt using Reactor command field names."""
        return {"chunk": self.chunk, "prompt": self.prompt}


@dataclass(frozen=True, slots=True)
class HeliosRequest(VideoInputs):
    """Helios conditioning and prompt changes.

    Attributes:
        prompts: Prompt changes scheduled during generation.

    """

    prompts: tuple[ScheduledPrompt, ...] = ()


__all__ = ["HeliosRequest", "ScheduledPrompt"]
