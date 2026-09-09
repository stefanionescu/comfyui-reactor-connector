"""Copied video frames and completed capture records."""

from pathlib import Path
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VideoFrame:
    """An owned RGB frame and its sender timestamp."""

    pixels: bytes
    width: int
    height: int
    timestamp_us: int


@dataclass(frozen=True, slots=True)
class CaptureResult:
    """File path, frame count, and timing method for the saved recording."""

    path: Path
    frames: int
    timestamp_mode: str
    audio_path: Path | None = None


__all__ = ["CaptureResult", "VideoFrame"]
