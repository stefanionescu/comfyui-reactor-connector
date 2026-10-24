"""Helios request and scheduled prompt records."""

from dataclasses import dataclass

from .inputs import VideoInputs


@dataclass(frozen=True, slots=True)
class ScheduledPrompt:
    """A later prompt on Helios's chunk clock.

    Attributes:
        chunk: Chunk at which the prompt changes.
        prompt: Scene text for subsequent generation.

    """

    chunk: int
    prompt: str


@dataclass(frozen=True, slots=True)
class HeliosRequest(VideoInputs):
    """Helios conditioning and prompt changes.

    Attributes:
        prompts: Prompt changes scheduled during generation.

    """

    prompts: tuple[ScheduledPrompt, ...] = ()
