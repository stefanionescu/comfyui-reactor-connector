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
        duration_seconds: Selected recording duration.
        max_output_bytes: Encoded output byte limit.
        max_memory_bytes: Decoded sample byte limit.
        start_seconds: Selected recording start.

    """

    source: Path
    destination: Path
    wav: Path
    duration_seconds: float
    max_output_bytes: int
    max_memory_bytes: int
    start_seconds: float


__all__ = ["RecordingManifest", "RecordingSettings", "RecordingVideo"]
