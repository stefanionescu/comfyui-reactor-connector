"""Fast H3 request and clip result values."""

from .inputs import VideoInputs
from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class FastGenerateRequest(VideoInputs):
    """A Fast H3 request with image endpoints and an aspect ratio.

    Attributes:
        aspect: Requested output aspect ratio.
        ending_image: Optional encoded ending image.

    """

    aspect: str
    ending_image: bytes | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class FastContinueRequest(FastGenerateRequest):
    """A sequence of clips linked by their final frames.

    Attributes:
        clip_seconds: Duration of each generated clip.
        clip_count: Number of clips to generate.
        later_prompts: Prompts for subsequent clips.

    """

    clip_seconds: float
    clip_count: int
    later_prompts: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class FastClip:
    """A generated clip and its reported timing and readiness.

    Attributes:
        clip_id: Provider clip identifier.
        seconds: Accepted clip duration.
        frames: Accepted frame count.
        ready: Whether clip generation is complete.

    """

    clip_id: str
    seconds: float
    frames: int
    ready: bool


__all__ = ["FastClip", "FastContinueRequest", "FastGenerateRequest"]
