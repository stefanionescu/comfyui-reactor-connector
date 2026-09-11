"""Index reviewed model capabilities by model key and provider connection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast, Literal, TYPE_CHECKING
from ..config.models.identities import MODEL_IDENTITIES

if TYPE_CHECKING:
    from typing import TypedDict

    class _ModelRecord(TypedDict):
        """One declarative model identity and its live-control policy."""

        guide_slug: str
        connection_name: str
        title: str
        max_prompt_characters: int
        prompt_kind: Literal["scene", "edit"]
        is_empty_prompt_allowed: bool
        camera_axes: tuple[str, ...]
        prompt_command: str
        has_audio_prompt: bool
        has_pointer: bool
        has_prompt_passthrough: bool


@dataclass(frozen=True, slots=True)
class ModelDefinition:
    """One reviewed model identity and its static live-control policy.

    Attributes:
        guide_slug: Public guide name used to build documentation links.
        connection_name: Provider connection selected for execution.
        title: Human-readable model name shown in connector interfaces.
        max_prompt_characters: Maximum prompt characters accepted during a live session.
        prompt_kind: Prompt editor language used by the live panel.
        is_empty_prompt_allowed: Whether a live prompt may contain only whitespace.
        camera_axes: Camera axes exposed by an interactive world model.
        prompt_command: Provider command used to update the main prompt.
        has_audio_prompt: Whether live sound prompting is available.
        has_pointer: Whether live pointer controls are available.
        has_prompt_passthrough: Whether prompt updates retain passthrough mode.

    """

    guide_slug: str
    connection_name: str
    title: str
    max_prompt_characters: int
    prompt_kind: Literal["scene", "edit"] = "scene"
    is_empty_prompt_allowed: bool = False
    camera_axes: tuple[str, ...] = ()
    prompt_command: str = "set_prompt"
    has_audio_prompt: bool = False
    has_pointer: bool = False
    has_prompt_passthrough: bool = False


MODELS: dict[str, ModelDefinition] = {
    name: ModelDefinition(**cast("_ModelRecord", record)) for name, record in MODEL_IDENTITIES.items()
}
MODELS_BY_CONNECTION: dict[str, ModelDefinition] = {
    definition.connection_name: definition for definition in MODELS.values()
}

__all__ = ["MODELS", "MODELS_BY_CONNECTION", "ModelDefinition"]
