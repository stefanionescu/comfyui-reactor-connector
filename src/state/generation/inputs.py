"""Shared immutable video request values."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True, slots=True)
class VideoInputs:
    """Shared capture inputs; adapters enforce their model restrictions.

    Attributes:
        prompt: Opening text sent to the model.
        duration_seconds: Requested recording length in seconds.
        seed: Random seed sent to the model.
        image: Optional encoded opening image.

    """

    prompt: str
    duration_seconds: float
    seed: int
    image: bytes | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class SourceVideoInputs(VideoInputs):
    """Shared inputs of the models that edit a source video file or a live camera.

    Attributes:
        video: Optional prepared source video path.

    """

    video: Path | None = None
