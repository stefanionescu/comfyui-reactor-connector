"""The recording interval selected while Fast H3 generates clips."""

from dataclasses import dataclass


@dataclass(slots=True)
class FastRecording:
    """The selected recording interval and its permitted extension for Fast H3 clips."""

    start_seconds: float = 0
    duration_seconds: float = 0
    maximum_seconds: float = 0


__all__ = ["FastRecording"]
