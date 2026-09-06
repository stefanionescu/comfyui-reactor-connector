"""Describe the PyAV writer boundary for static checks only."""

from contextlib import AbstractContextManager
from fractions import Fraction
from typing import Literal, Protocol, overload

import av


class AudioStream(Protocol):
    layout: str
    time_base: Fraction

    def encode(self, frame: av.AudioFrame | None) -> list[object]: ...


class VideoStream(Protocol):
    width: int
    height: int
    pix_fmt: str
    time_base: Fraction
    codec_context: av.VideoCodecContext
    options: dict[str, str]

    def encode(self, frame: av.VideoFrame | None) -> list[object]: ...


class MediaWriter(AbstractContextManager["MediaWriter"], Protocol):
    @overload
    def add_stream(self, codec: Literal["aac"], *, rate: int) -> AudioStream: ...

    @overload
    def add_stream(self, codec: Literal["libx264"], *, rate: Fraction) -> VideoStream: ...

    def mux(self, packet: object) -> None: ...
