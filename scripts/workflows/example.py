"""Describe named node inputs and the connections included in one workflow."""

from typing import Literal
from dataclasses import dataclass
from ...config.models.nodes import NODE_MODELS
from ...src.language import read_messages, translate


@dataclass(frozen=True, slots=True)
class Example:
    """One editable workflow with named widget values and explicit media sources."""

    slug: str
    node_id: str
    inputs: dict[str, str | float | bool]
    sources: tuple[str, ...] = ()
    plan: Literal["none", "prompts", "shots"] = "none"
    mode: Literal["record", "world", "live", "webcam"] = "record"

    @property
    def title(self) -> str:
        """Read the example title from the workflow language file."""
        return translate("workflows", self.slug + ".title")

    @property
    def widgets(self) -> dict[str, str | float | bool]:
        """Combine model controls with the example's editable text."""
        values = self.inputs.copy()
        messages = read_messages("workflows")
        for name in ("prompt", "audio_prompt", "script", "later_prompts"):
            key = self.slug + "." + name
            if key in messages:
                values[name] = translate("workflows", key)
        return values

    @property
    def model(self) -> str:
        """Return the model associated with the registered node."""
        return NODE_MODELS[self.node_id]

    @property
    def clip_count(self) -> int:
        """Return the number of clips explicitly requested by a continuation example."""
        return int(self.inputs.get("clip_count", 1))

    @property
    def duration_seconds(self) -> float:
        """Return the total video duration for one clip or a continued sequence."""
        if "clip_seconds" in self.inputs:
            return float(self.inputs["clip_seconds"]) * self.clip_count
        return float(self.inputs["duration_seconds"])

    @property
    def path(self) -> str:
        """Group editable examples by the model used for generation."""
        return f"{self.model}/{self.slug}.json"
