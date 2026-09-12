"""Reviewed model capability records."""

from typing import Literal
from dataclasses import dataclass


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


__all__ = ["ModelDefinition"]
