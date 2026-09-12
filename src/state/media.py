"""Copied video frames and completed capture records."""

from pathlib import Path
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VideoFrame:
    """An owned RGB frame and its sender timestamp.

    Attributes:
        pixels: Packed RGB pixel bytes.
        width: Frame width in pixels.
        height: Frame height in pixels.
        timestamp_us: Sender timestamp in microseconds.

    """

    pixels: bytes
    width: int
    height: int
    timestamp_us: int


@dataclass(frozen=True, slots=True)
class CaptureResult:
    """File and timing facts for a completed recording.

    Attributes:
        path: Saved recording path.
        frames: Encoded frame count.
        timestamp_mode: Timing source used during capture.
        audio_path: Optional temporary audio file.

    """

    path: Path
    frames: int
    timestamp_mode: str
    audio_path: Path | None = None


__all__ = ["CaptureResult", "VideoFrame"]
