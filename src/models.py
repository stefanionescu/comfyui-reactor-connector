"""Index reviewed model capabilities by model key and provider connection."""

from __future__ import annotations

from .state.models import ModelDefinition
from ..config.models import MODEL_IDENTITIES
from typing import cast, Literal, TYPE_CHECKING

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


MODELS: dict[str, ModelDefinition] = {
    name: ModelDefinition(**cast("_ModelRecord", record)) for name, record in MODEL_IDENTITIES.items()
}
MODELS_BY_CONNECTION: dict[str, ModelDefinition] = {
    definition.connection_name: definition for definition in MODELS.values()
}


__all__ = ["MODELS", "MODELS_BY_CONNECTION"]
