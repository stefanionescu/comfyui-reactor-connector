"""Prompt, sound, and webcam options for one live session."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from ..media.webcam import WebcamFrames


@dataclass(frozen=True, slots=True)
class LiveOptions:
    """Prompts, sound options, and optional webcam input for a live session.

    Attributes:
        connection_name: Reviewed provider model connection.
        prompt: Opening scene or edit prompt.
        webcam: Optional browser frame source.
        is_passthrough_enabled: Whether prompt changes pass through immediately.
        audio_prompt: Opening sound prompt.
        is_audio_enabled: Whether generated audio is enabled.

    """

    connection_name: str
    prompt: str
    webcam: WebcamFrames | None = None
    is_passthrough_enabled: bool = False
    audio_prompt: str = ""
    is_audio_enabled: bool = False


__all__ = ["LiveOptions"]
