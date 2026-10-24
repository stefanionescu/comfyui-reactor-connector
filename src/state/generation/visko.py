"""Visko image, sound, and prompt request values."""

from dataclasses import dataclass

from .inputs import VideoInputs


@dataclass(frozen=True, slots=True)
class ViskoRequest(VideoInputs):
    """Synchronized image and sound generation settings.

    Attributes:
        audio_prompt: Text describing the requested sound.
        resolution: Requested provider resolution.
        audio_enabled: Whether the model generates sound.
        prompt_passthrough: Whether to send prompts without preprocessing.

    """

    audio_prompt: str = ''
    resolution: str = ''
    audio_enabled: bool = True
    prompt_passthrough: bool = False
