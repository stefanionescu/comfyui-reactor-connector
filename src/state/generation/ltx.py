"""Portrait speech request values."""

from .inputs import VideoInputs
from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class LtxSpeakRequest(VideoInputs):
    """Portrait and speech conditions for one take.

    Attributes:
        words_per_minute: Requested speech rate.
        script: Speech text sent to the provider.

    """

    words_per_minute: int
    script: str = ""


__all__ = ["LtxSpeakRequest"]
