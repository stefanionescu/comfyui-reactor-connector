"""SANA source and editing request values."""

from __future__ import annotations

from .inputs import VideoInputs
from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True, slots=True, kw_only=True)
class SanaRequest(VideoInputs):
    """Source selection and edit controls.

    Attributes:
        anchor_interval: Number of chunks between anchors.
        video: Optional prepared source video path.

    """

    anchor_interval: int
    video: Path | None = None


__all__ = ["SanaRequest"]
