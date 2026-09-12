"""LongLive request and storyboard records."""

from .inputs import VideoInputs
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Shot:
    """A prompt change on the provider's cumulative chunk clock.

    Attributes:
        at_session_chunk: Chunk at which the shot begins.
        transition: Provider transition choice.
        prompt: Scene text for the shot.

    """

    at_session_chunk: int
    transition: str
    prompt: str

    def to_dict(self) -> dict[str, object]:
        """Encode the shot using Reactor storyboard field names."""
        return {
            "at_session_chunk": self.at_session_chunk,
            "transition": self.transition,
            "prompt": self.prompt,
        }


@dataclass(frozen=True, slots=True)
class LongLiveRequest(VideoInputs):
    """Opening conditions and ordered later shots.

    Attributes:
        shots: Ordered shots to stage before generation.

    """

    shots: tuple[Shot, ...] = ()


__all__ = ["LongLiveRequest", "Shot"]
