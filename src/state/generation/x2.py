"""X2 source, reference, and pointer request values."""

from __future__ import annotations

from .inputs import VideoInputs
from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True, slots=True, kw_only=True)
class X2Request(VideoInputs):
    """Edit controls for a file or live camera source.

    Attributes:
        pointer_x: Normalized horizontal pointer position.
        pointer_y: Normalized vertical pointer position.
        video: Optional prepared source video path.
        keep_backlog: Whether the provider retains queued source frames.
        pointer_active: Whether pointer control starts active.

    """

    pointer_x: float
    pointer_y: float
    video: Path | None = None
    keep_backlog: bool = False
    pointer_active: bool = False


__all__ = ["X2Request"]
