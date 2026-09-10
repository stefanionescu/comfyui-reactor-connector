"""Describe the PyAV writer boundary for static checks only."""

import av
from fractions import Fraction
from contextlib import AbstractContextManager
from typing import Literal, overload, Protocol


class AudioStream(Protocol):
    """Audio encoder layout, clock, and packet operations used by the recording worker."""

    layout: str
    time_base: Fraction

    def encode(self, frame: av.AudioFrame | None) -> list[object]:
        """Encode one audio frame, or flush pending packets when the frame is None."""
        raise NotImplementedError


class VideoStream(Protocol):
    """Video encoder fields and packet operations used by the local media worker."""

    width: int
    height: int
    pix_fmt: str
    time_base: Fraction
    codec_context: av.VideoCodecContext
    options: dict[str, str]

    def encode(self, frame: av.VideoFrame | None) -> list[object]:
        """Encode one video frame, or flush pending packets when the frame is None."""
        raise NotImplementedError


class MediaWriter(AbstractContextManager["MediaWriter"], Protocol):
    """Audio and video stream operations used to assemble the final recording."""

    @overload
    def add_stream(self, _codec: Literal["aac"], /, *, rate: int) -> AudioStream:
        """Create the selected audio or video encoder with its output rate."""
        raise NotImplementedError

    @overload
    def add_stream(self, _codec: Literal["libx264"], /, *, rate: Fraction) -> VideoStream:
        """Create the selected audio or video encoder with its output rate."""
        raise NotImplementedError

    def mux(self, packet: object) -> None:
        """Write an encoded packet into the combined recording."""
        raise NotImplementedError
