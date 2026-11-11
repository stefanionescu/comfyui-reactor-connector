"""Encode framed red, green, and blue (RGB) input in a standalone, terminable worker process."""

from __future__ import annotations

import sys
import json
import struct
from typing import TYPE_CHECKING, BinaryIO, cast
from pathlib import Path
from fractions import Fraction

import av
import numpy as np

from src.state.workers import EncoderSettings

from ..config.media.video import ENCODER_CRF, ENCODER_NAME, ENCODER_PRESET, ENCODER_PIXEL_FORMAT
from ..config.media.images import RGB_CHANNELS
from ..config.media.capture import FRAME_HEADER_FORMAT, MAX_FRAME_DIMENSION, MIN_FRAME_DIMENSION

if TYPE_CHECKING:
    from av.packet import Packet
    from av.video.stream import VideoStream
    from av.container.output import OutputContainer

WORKER_ARGUMENT_COUNT = 6

FRAME_HEADER = struct.Struct(FRAME_HEADER_FORMAT)


class EncodingError(Exception):
    """Carry a fixed protocol code without exposing native error text."""


def _receive(source: BinaryIO, limit: int) -> tuple[int, int, int, bytes] | None:
    """Read one framed RGB payload and reject truncated or oversized input.

    Args:
        source: The stream that holds the framed payload.
        limit: The largest pixel payload to accept, in bytes.

    Returns:
        The width, height, timestamp, and pixels, or None when the stream has ended.

    Raises:
        EncodingError: When the payload is truncated or its size is out of range.

    """
    header = source.read(FRAME_HEADER.size)
    if not header:
        return None
    if len(header) != FRAME_HEADER.size:
        message = 'truncated'
        raise EncodingError(message)
    width, height, timestamp = cast('tuple[int, int, int]', FRAME_HEADER.unpack(header))
    size = width * height * RGB_CHANNELS
    if (
        not (
            MIN_FRAME_DIMENSION <= width <= MAX_FRAME_DIMENSION and MIN_FRAME_DIMENSION <= height <= MAX_FRAME_DIMENSION
        )
        or width % 2
        or height % 2
        or size > limit
    ):
        message = 'frame_size'
        raise EncodingError(message)
    pixels = source.read(size)
    if len(pixels) != size:
        message = 'truncated'
        raise EncodingError(message)
    return width, height, timestamp, pixels


def _mux(container: OutputContainer, packets: list[Packet[VideoStream]], settings: EncoderSettings) -> None:
    """Write encoded packets while enforcing the output file limit.

    Args:
        container: The output file that receives the packets.
        packets: The encoded packets to write.
        settings: The settings that hold the output path and its size limit.

    Raises:
        EncodingError: When the file exceeds its size limit.

    """
    for packet in packets:
        container.mux(packet)  # pyright: ignore[reportUnknownMemberType] # reason: PyAV's stubs leave Packet without its stream type.
        if settings.path.stat().st_size > settings.output_bytes:
            message = 'file_limit'
            raise EncodingError(message)


def _encode_frames(
    source: BinaryIO, container: OutputContainer, stream: VideoStream, settings: EncoderSettings
) -> tuple[int, str]:
    """Encode increasing timestamps within the requested duration and flush the final packets.

    Args:
        source: The stream of framed input.
        container: The output file to write.
        stream: The video stream that encodes each frame.
        settings: The settings that hold the duration, frame rate, and limits.

    Returns:
        The frame count and the timestamp mode.

    Raises:
        EncodingError: When frames are missing, change size, or have timestamps that do not increase.

    """
    first_timestamp: int | None = None
    previous_pts = -1
    frame_count = 0
    timestamp_mode = 'sender'
    while (received := _receive(source, settings.frame_bytes)) is not None:
        width, height, timestamp, pixels = received
        if first_timestamp is None:
            first_timestamp = timestamp
            timestamp_mode = 'sender' if timestamp > 0 else 'fallback_fps'
            stream.width, stream.height = width, height
        if (stream.width, stream.height) != (width, height):
            message = 'dimensions'
            raise EncodingError(message)
        pts = (
            timestamp - first_timestamp if timestamp_mode == 'sender' else round(frame_count * 1_000_000 / settings.fps)
        )
        if pts <= previous_pts:
            message = 'timestamps'
            raise EncodingError(message)
        if pts >= settings.duration_us:
            break
        array = np.frombuffer(pixels, dtype=np.uint8).reshape(height, width, RGB_CHANNELS)
        frame = av.VideoFrame.from_ndarray(array, format='rgb24')
        frame.pts, frame.time_base = pts, Fraction(1, 1_000_000)
        _mux(container, stream.encode(frame), settings)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType] # reason: PyAV's stubs leave Packet without its stream type.
        previous_pts = pts
        frame_count += 1
    if not frame_count:
        message = 'no_frames'
        raise EncodingError(message)
    _mux(container, stream.encode(), settings)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType] # reason: PyAV's stubs leave Packet without its stream type.
    return frame_count, timestamp_mode


def encode(source: BinaryIO, settings: EncoderSettings) -> dict[str, str | int]:
    """Write an MP4 within the recording limits and report its size, timing, or errors.

    Args:
        source: The binary stream that delivers the frames.
        settings: The output path, timing, and limits of the encoder.

    Returns:
        The frame count and the timestamp mode of the file.

    Raises:
        EncodingError: When the finished file exceeds its size limit.

    """
    with av.open(str(settings.path), mode='w', format='mp4') as container:
        stream = container.add_stream(ENCODER_NAME, rate=Fraction(settings.fps), pix_fmt=ENCODER_PIXEL_FORMAT)  # pyright: ignore[reportUnknownMemberType] # reason: PyAV's stubs leave Packet without its stream type.
        stream.time_base = Fraction(1, 1_000_000)
        stream.codec_context.time_base = Fraction(1, 1_000_000)
        stream.options = {'preset': ENCODER_PRESET, 'crf': ENCODER_CRF}
        sys.stdout.write(json.dumps({'ready': True}) + '\n')
        sys.stdout.flush()
        frames, mode = _encode_frames(source, container, stream, settings)
    if settings.path.stat().st_size > settings.output_bytes:
        message = 'file_limit'
        raise EncodingError(message)
    return {'frames': frames, 'timestamp_mode': mode}


def read_settings(arguments: list[str]) -> EncoderSettings:
    """Parse the fixed capture worker command and require positive encoding limits.

    Args:
        arguments: The command line of the capture worker, with the program name first.

    Returns:
        The parsed encoder settings.

    Raises:
        ValueError: When the argument count is wrong or a limit is below one.

    """
    if len(arguments) != WORKER_ARGUMENT_COUNT:
        raise ValueError
    settings = EncoderSettings(
        path=Path(arguments[1]),
        duration_us=int(arguments[2]),
        frame_bytes=int(arguments[3]),
        output_bytes=int(arguments[4]),
        fps=int(arguments[5]),
    )
    if min(settings.duration_us, settings.frame_bytes, settings.output_bytes, settings.fps) < 1:
        raise ValueError
    return settings
