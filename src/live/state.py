"""Live-control options and queued browser input records."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

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

    connection_name: str
    prompt: str
    webcam: WebcamFrames | None = None
    is_passthrough_enabled: bool = False
    audio_prompt: str = ""
    is_audio_enabled: bool = False


__all__ = ["BrowserInput", "CameraChange", "LiveOptions"]
