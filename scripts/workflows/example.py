"""Describe named node inputs and the connections included in one workflow."""

from typing import Literal
from dataclasses import dataclass
from ...src.language import translate


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
        """Name the directly discoverable native workflow file."""
        return f"{self.slug}.json"
