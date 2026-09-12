"""Shared immutable video request values."""

from dataclasses import dataclass


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


__all__ = ["VideoInputs"]
