"""Live-control options and queued browser input records."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass
from ...config.generation import fast, session, video, world

if TYPE_CHECKING:
    from ..media.webcam import WebcamFrames


@dataclass(frozen=True, slots=True)
class BrowserInput:
    """Camera directions and their sequence number."""

    sequence: int
    axes: tuple[tuple[str, str], ...]
    end: bool
    received_at: float = 0.0
    release: bool = False


@dataclass(frozen=True, slots=True)
class CameraChange:
    """One requested camera value and the time it entered the command queue."""

    value: str
    queued_at: float


@dataclass(frozen=True, slots=True)
class LiveOptions:
    """Model-specific prompts, sound options, and optional webcam input for a live session."""

    model: str
    prompt: str
    webcam: WebcamFrames | None = None
    passthrough: bool = False
    audio_prompt: str = ""
    audio_enabled: bool = True

    @property
    def prompt_limit(self) -> int:
        """Return the prompt character limit for the selected model."""
        if self.model == "reactor/fast-h3":
            return fast.MAX_PROMPT_CHARACTERS
        if self.model in ("reactor/lingbot", "reactor/lingbot-world-2"):
            return world.MAX_WORLD_PROMPT_CHARACTERS
        if self.model == "xmax/x2":
            return video.MAX_EDIT_PROMPT_CHARACTERS
        return session.MAX_PROMPT_CHARACTERS


__all__ = ["BrowserInput", "CameraChange", "LiveOptions"]
