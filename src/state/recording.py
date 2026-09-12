"""Host-free recording fragment and encoding records."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from pathlib import Path
    from fractions import Fraction


@dataclass(frozen=True, slots=True)
class RecordingManifest:
    """Validated initialization and recording fragment URLs.

    Attributes:
        initialization: Initialization fragment URL.
        segments: Ordered recording fragment URLs.

    """

    initialization: str
    segments: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RecordingVideo:
    """Timing and dimensions used for recording conversion.

    Attributes:
        origin: Recording timestamp origin.
        rate: Video frame rate.
        width: Frame width in pixels.
        height: Frame height in pixels.

    """

    origin: Fraction
    rate: Fraction
    width: int
    height: int


@dataclass(frozen=True, slots=True)
class RecordingSettings:
    """Local recording paths, selected interval, and size limits.

    Attributes:
        source: Local fragmented recording source.
        destination: Encoded video destination.
        wav: Separate audio destination.
        duration: Selected recording duration.
        size_limit: Encoded output byte limit.
        memory_limit: Decoded sample byte limit.
        start_seconds: Selected recording start.

    """

    source: Path
    destination: Path
    wav: Path
    duration: float
    size_limit: int
    memory_limit: int
    start_seconds: float


__all__ = ["RecordingManifest", "RecordingSettings", "RecordingVideo"]
