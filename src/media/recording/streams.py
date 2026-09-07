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
        # codeql[py/ineffectual-statement] -- reason: Protocol method declaration.
        ...


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
        # codeql[py/ineffectual-statement] -- reason: Protocol method declaration.
        ...


class MediaWriter(AbstractContextManager["MediaWriter"], Protocol):
    """Audio and video stream operations used to assemble the final recording."""

    @overload
    def add_stream(self, _codec: Literal["aac"], /, *, rate: int) -> AudioStream:
        """Create the selected audio or video encoder with its output rate."""
        # codeql[py/ineffectual-statement] -- reason: Protocol method declaration.
        ...

    @overload
    def add_stream(self, _codec: Literal["libx264"], /, *, rate: Fraction) -> VideoStream:
        """Create the selected audio or video encoder with its output rate."""
        # codeql[py/ineffectual-statement] -- reason: Protocol method declaration.
        ...

    def mux(self, packet: object) -> None:
        """Write an encoded packet into the combined recording."""
        # codeql[py/ineffectual-statement] -- reason: Protocol method declaration.
        ...
