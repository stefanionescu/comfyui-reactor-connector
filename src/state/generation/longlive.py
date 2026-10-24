"""LongLive request and storyboard records."""

from dataclasses import dataclass

from .inputs import VideoInputs


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


@dataclass(frozen=True, slots=True)
class LongLiveRequest(VideoInputs):
    """Opening conditions and ordered later shots.

    Attributes:
        shots: Ordered shots to stage before generation.

    """

    shots: tuple[Shot, ...] = ()
