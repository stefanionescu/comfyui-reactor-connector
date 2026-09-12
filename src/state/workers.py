"""Host-free settings for isolated media workers."""

from pathlib import Path
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EncoderSettings:
    """Non-secret capture limits supplied to the encoder.

    Attributes:
        path: Destination recording path.
        duration_us: Maximum recording duration in microseconds.
        frame_bytes: Maximum bytes in one decoded frame.
        output_bytes: Maximum encoded output size.
        fps: Fallback frame rate.

    """

    path: Path
    duration_us: int
    frame_bytes: int
    output_bytes: int
    fps: int


@dataclass(frozen=True, slots=True)
class SourceSettings:
    """Local source paths, interval, and limits for video preparation.

    Attributes:
        source: Local source media path.
        destination: Prepared video path.
        start_seconds: Selected source start.
        duration_seconds: Maximum selected duration.
        maximum_bytes: Maximum encoded output bytes.
        frame_bytes: Maximum decoded frame bytes.

    """

    source: Path
    destination: Path
    start_seconds: float
    duration_seconds: float
    maximum_bytes: int
    frame_bytes: int


__all__ = ["EncoderSettings", "SourceSettings"]
