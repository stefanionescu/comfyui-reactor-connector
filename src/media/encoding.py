"""Encode framed RGB input in a standalone, terminable worker process."""

import av
import sys
import json
import struct
import numpy as np
from pathlib import Path
from fractions import Fraction
from ..language import translate
from dataclasses import dataclass
from typing import cast, BinaryIO, Protocol
from contextlib import AbstractContextManager
from config.media.capture import FRAME_HEADER_FORMAT, MAX_FRAME_DIMENSION, MIN_FRAME_DIMENSION


WORKER_ARGUMENT_COUNT = 6

FRAME_HEADER = struct.Struct(FRAME_HEADER_FORMAT)


class VideoCodecContext(Protocol):
    """Keep sender timestamp precision in the encoder's clock."""

    time_base: Fraction


class VideoStream(Protocol):
    """The encoder fields and packets used by incremental RGB capture."""

    width: int
    height: int
    pix_fmt: str
    time_base: Fraction
    options: dict[str, str]
    codec_context: VideoCodecContext

    def encode(self, frame: av.VideoFrame | None = None) -> list[object]:
        """Encode one video frame, or flush pending packets when the frame is None."""
        # codeql[py/ineffectual-statement] -- reason: Protocol method declaration.
        ...


class VideoContainer(AbstractContextManager["VideoContainer"], Protocol):
    """The output-container operations used by the capture worker."""

    def add_stream(self, _codec_name: str, /, rate: Fraction) -> VideoStream:
        """Create an encoder for the selected video codec and frame rate."""
        # codeql[py/ineffectual-statement] -- reason: Protocol method declaration.
        ...

    def mux(self, packet: object) -> None:
        """Write an encoded packet into the output container."""
        # codeql[py/ineffectual-statement] -- reason: Protocol method declaration.
        ...


class EncodingError(Exception):
    """Carry a fixed protocol code without exposing native error text."""


@dataclass(frozen=True, slots=True)
class EncoderSettings:
    """Non-secret limits passed by the owning connector process."""

    path: Path
    duration_us: int
    frame_bytes: int
    output_bytes: int
    fps: int


def _receive(source: BinaryIO, limit: int) -> tuple[int, int, int, bytes] | None:
    """Read one framed RGB payload and reject truncated or oversized input."""
    header = source.read(FRAME_HEADER.size)
    if not header:
        return None
    if len(header) != FRAME_HEADER.size:
        msg = "truncated"
        raise EncodingError(msg)
    width, height, timestamp = cast("tuple[int, int, int]", FRAME_HEADER.unpack(header))
    size = width * height * 3
    if (
        not (
            MIN_FRAME_DIMENSION <= width <= MAX_FRAME_DIMENSION and MIN_FRAME_DIMENSION <= height <= MAX_FRAME_DIMENSION
        )
        or width % 2
        or height % 2
        or size > limit
    ):
        msg = "frame_size"
        raise EncodingError(msg)
    pixels = source.read(size)
    if len(pixels) != size:
        msg = "truncated"
        raise EncodingError(msg)
    return width, height, timestamp, pixels


def _mux(container: VideoContainer, packets: list[object], settings: EncoderSettings) -> None:
    """Write encoded packets while enforcing the output file limit."""
    for packet in packets:
        container.mux(packet)
        if settings.path.stat().st_size > settings.output_bytes:
            msg = "file_limit"
            raise EncodingError(msg)


def _encode_frames(
    source: BinaryIO, container: VideoContainer, stream: VideoStream, settings: EncoderSettings
) -> tuple[int, str]:
    """Encode increasing timestamps within the requested duration and flush the final packets."""
    first_timestamp: int | None = None
    previous_pts = -1
    frame_count = 0
    timestamp_mode = "sender"
    while (received := _receive(source, settings.frame_bytes)) is not None:
        width, height, timestamp, pixels = received
        if first_timestamp is None:
            first_timestamp = timestamp
            timestamp_mode = "sender" if timestamp > 0 else "fallback_fps"
            stream.width, stream.height = width, height
        if (stream.width, stream.height) != (width, height):
            msg = "dimensions"
            raise EncodingError(msg)
        pts = (
            timestamp - first_timestamp if timestamp_mode == "sender" else round(frame_count * 1_000_000 / settings.fps)
        )
        if pts <= previous_pts:
            msg = "timestamps"
            raise EncodingError(msg)
        if pts >= settings.duration_us:
            break
        array = np.frombuffer(pixels, dtype=np.uint8).reshape(height, width, 3)
        frame = av.VideoFrame.from_ndarray(array, format="rgb24")
        frame.pts, frame.time_base = pts, Fraction(1, 1_000_000)
        _mux(container, stream.encode(frame), settings)
        previous_pts = pts
        frame_count += 1
    if not frame_count:
        msg = "no_frames"
        raise EncodingError(msg)
    _mux(container, stream.encode(), settings)
    return frame_count, timestamp_mode


def encode(source: BinaryIO, settings: EncoderSettings) -> dict[str, str | int]:
    """Write an MP4 within the recording limits and report its size, timing, or errors."""
    output = cast("VideoContainer", av.open(str(settings.path), mode="w", format="mp4"))
    with output as container:
        stream = container.add_stream("libx264", rate=Fraction(settings.fps))
        stream.pix_fmt = "yuv420p"
        stream.time_base = Fraction(1, 1_000_000)
        stream.codec_context.time_base = Fraction(1, 1_000_000)
        stream.options = {"preset": "veryfast", "crf": "18"}
        sys.stdout.write(str(json.dumps({"ready": True})) + "\n")
        sys.stdout.flush()
        frames, mode = _encode_frames(source, container, stream, settings)
    if settings.path.stat().st_size > settings.output_bytes:
        msg = "file_limit"
        raise EncodingError(msg)
    return {"frames": frames, "timestamp_mode": mode}


def read_settings(arguments: list[str]) -> EncoderSettings:
    """Parse the fixed capture worker command and require positive encoding limits."""
    if len(arguments) != WORKER_ARGUMENT_COUNT:
        msg = translate("main", "errors.workerArguments")
        raise ValueError(msg)
    settings = EncoderSettings(Path(arguments[1]), *(int(value) for value in arguments[2:]))
    if min(settings.duration_us, settings.frame_bytes, settings.output_bytes, settings.fps) < 1:
        msg = translate("main", "errors.workerLimits")
        raise ValueError(msg)
    return settings


def main(arguments: list[str]) -> int:
    """Run only as an explicitly launched worker; do not import the ComfyUI host."""
    try:
        result = encode(sys.stdin.buffer, read_settings(arguments))
    except EncodingError as error:
        sys.stdout.write(str(json.dumps({"error": str(error)})) + "\n")
        sys.stdout.flush()
        return 1
    except Exception:  # noqa: BLE001 -- reason: The worker protocol permits only fixed error codes, never native exception text.
        sys.stdout.write(str(json.dumps({"error": "encoder_failed"})) + "\n")
        sys.stdout.flush()
        return 1
    sys.stdout.write(str(json.dumps(result)) + "\n")
    sys.stdout.flush()
    return 0
