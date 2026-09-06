"""Describe the inputs and notes included in one portable workflow."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Example:
    slug: str
    title: str
    node_id: str
    model: str
    prompt: str
    image: bool = False
    storyboard: bool = False
    prompt_sequence: bool = False
    controls: tuple[str | float | bool, ...] = ()
    video: bool = False
    seed: bool = True
    reference: bool = False
    audio: bool = False
    duration_seconds: float = 5.0
    ending_image: bool = False
    interactive: bool = False
    panel: bool = False
    webcam: bool = False
    clip_count: int = 1

    @property
    def path(self) -> str:
        """Group editable examples by the model used for generation."""
        return f"{self.model}/{self.slug}.json"
