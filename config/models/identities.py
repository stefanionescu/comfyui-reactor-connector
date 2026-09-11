"""Describe reviewed Reactor model identities and live capabilities."""

from dataclasses import dataclass
from typing import Literal

from ..generation.fast import MAX_PROMPT_CHARACTERS as MAX_FAST_PROMPT_CHARACTERS
from ..generation.session import MAX_PROMPT_CHARACTERS
from ..generation.video import MAX_EDIT_PROMPT_CHARACTERS
from ..generation.world import LINGBOT_CAMERA_AXES, LINGBOT_WORLD_CAMERA_AXES, MAX_WORLD_PROMPT_CHARACTERS


@dataclass(frozen=True, slots=True)
class ModelDefinition:
    """One reviewed model identity and its static live-control policy.

    Attributes:
        guide_slug: Public guide name used to build documentation links.
        connection_name: Provider connection selected for execution.
        title: Human-readable model name shown in connector interfaces.
        prompt_limit: Maximum prompt characters accepted during a live session.
        prompt_kind: Prompt editor language used by the live panel.
        allow_empty_prompt: Whether a live prompt may contain only whitespace.
        camera_axes: Camera axes exposed by an interactive world model.
        prompt_command: Provider command used to update the main prompt.
        supports_audio_prompt: Whether live sound prompting is available.
        supports_pointer: Whether live pointer controls are available.
        supports_prompt_passthrough: Whether prompt updates retain passthrough mode.
    """

    guide_slug: str
    connection_name: str
    title: str
    prompt_limit: int
    prompt_kind: Literal["scene", "edit"] = "scene"
    allow_empty_prompt: bool = False
    camera_axes: tuple[str, ...] = ()
    prompt_command: str = "set_prompt"
    supports_audio_prompt: bool = False
    supports_pointer: bool = False
    supports_prompt_passthrough: bool = False


MODELS: dict[str, ModelDefinition] = {
    "fast-h3": ModelDefinition(
        guide_slug="fast-h3",
        connection_name="reactor/fast-h3",
        title="Fast H3",
        prompt_limit=MAX_FAST_PROMPT_CHARACTERS,
    ),
    "visko-orbis-stable": ModelDefinition(
        guide_slug="visko-orbis-stable",
        connection_name="reactor/visko-orbis-stable",
        title="Visko Stable",
        prompt_limit=MAX_PROMPT_CHARACTERS,
        supports_audio_prompt=True,
        supports_prompt_passthrough=True,
    ),
    "visko-orbis-dynamic": ModelDefinition(
        guide_slug="visko-orbis-dynamic",
        connection_name="reactor/visko-orbis-dynamic",
        title="Visko Dynamic",
        prompt_limit=MAX_PROMPT_CHARACTERS,
        supports_audio_prompt=True,
        supports_prompt_passthrough=True,
    ),
    "helios": ModelDefinition(
        guide_slug="helios",
        connection_name="reactor/helios",
        title="Helios",
        prompt_limit=MAX_PROMPT_CHARACTERS,
    ),
    "lingbot": ModelDefinition(
        guide_slug="lingbot",
        connection_name="reactor/lingbot",
        title="LingBot",
        prompt_limit=MAX_WORLD_PROMPT_CHARACTERS,
        camera_axes=LINGBOT_CAMERA_AXES,
    ),
    "lingbot-world-2": ModelDefinition(
        guide_slug="lingbot-world-2",
        connection_name="reactor/lingbot-world-2",
        title="LingBot World 2",
        prompt_limit=MAX_WORLD_PROMPT_CHARACTERS,
        camera_axes=LINGBOT_WORLD_CAMERA_AXES,
    ),
    "longlive-v2": ModelDefinition(
        guide_slug="longlive-v2",
        connection_name="reactor/longlive-v2",
        title="LongLive",
        prompt_limit=MAX_PROMPT_CHARACTERS,
        prompt_command="set_shot",
    ),
    "sana-streaming": ModelDefinition(
        guide_slug="sana-streaming",
        connection_name="reactor/sana-streaming",
        title="SANA",
        prompt_limit=MAX_PROMPT_CHARACTERS,
        prompt_kind="edit",
        allow_empty_prompt=True,
    ),
    "ltx2": ModelDefinition(
        guide_slug="ltx",
        connection_name="reactor/ltx2",
        title="LTX",
        prompt_limit=MAX_PROMPT_CHARACTERS,
    ),
    "x2": ModelDefinition(
        guide_slug="x2",
        connection_name="xmax/x2",
        title="X2",
        prompt_limit=MAX_EDIT_PROMPT_CHARACTERS,
        prompt_kind="edit",
        supports_pointer=True,
    ),
}

MODELS_BY_CONNECTION: dict[str, ModelDefinition] = {
    definition.connection_name: definition for definition in MODELS.values()
}

__all__ = [
    "MODELS",
    "MODELS_BY_CONNECTION",
    "ModelDefinition",
]
