"""Prepare local video incrementally in a process the host can terminate."""

from pathlib import Path
from fractions import Fraction
from collections.abc import Iterator

import av
from av.video.stream import VideoStream
from av.container.input import InputContainer
from av.container.output import OutputContainer

from src.state.workers import SourceSettings

from ..protocol import report_ready_outcome
from ...config.media.video import (
    ENCODER_CRF,
    ENCODER_NAME,
    ENCODER_PRESET,
    MAX_FRAME_RATE,
    MIN_SOURCE_FRAMES,
    HDR_TRANSFER_CODES,
    MAX_COMPONENT_BITS,
    MAX_FRAME_DIMENSION,
    MIN_FRAME_DIMENSION,
    ENCODER_PIXEL_FORMAT,
)
from ...config.media.images import RGB_CHANNELS

SOURCE_WORKER_ARGUMENT_COUNT = 7


class SourceError(Exception):
    """Report a fixed code without exposing input paths or decoder messages."""


def prepare(settings: SourceSettings) -> dict[str, int | str]:
    """Write a video-only MP4, preserving source timing inside the selected interval.

    Args:
        settings: The source, destination, interval, and limits.

    Returns:
        The frame count and the timestamp mode.

    Raises:
        SourceError: When the source is unsupported or the output exceeds its size limit.

    """
    # A file handle keeps PyAV from reading an input string as a URL.
    # Restrict demuxers and protocols so playlists cannot fetch other resources.
    with (
        settings.source.open('rb') as file,
        av.open(
            file,
            mode='r',
            options={
                'format_whitelist': 'mov,matroska,webm,avi',
                'protocol_whitelist': 'pipe',
            },
        ) as reader,
        av.open(str(settings.destination), 'w', format='mp4') as writer,
    ):
        if len(reader.streams.video) != 1:
            message = 'source_streams'
            raise SourceError(message)
        input_stream = reader.streams.video[0]
        if input_stream.codec_context.color_trc in HDR_TRANSFER_CODES:
            message = 'source_hdr'
            raise SourceError(message)
        rate = input_stream.average_rate
        if rate is None or not 1 <= rate <= MAX_FRAME_RATE:
            message = 'source_rate'
            raise SourceError(message)
        output = writer.add_stream(ENCODER_NAME, rate=rate, pix_fmt=ENCODER_PIXEL_FORMAT)  # pyright: ignore[reportUnknownMemberType] # reason: PyAV's stubs leave Packet without its stream type.
        output.time_base = Fraction(1, 1_000_000)
        output.codec_context.time_base = output.time_base
        output.options = {'preset': ENCODER_PRESET, 'crf': ENCODER_CRF}
        frames = copy_frames(reader, output, writer, settings)

    if settings.destination.stat().st_size > settings.maximum_bytes:
        message = 'file_limit'
        raise SourceError(message)
    return {'frames': frames, 'timestamp_mode': 'sender'}


def validate_frame(frame: av.VideoFrame, output: VideoStream, frame_bytes: int) -> None:
    """Reject changing dimensions, oversized frames, and unsupported pixel depth.

    Args:
        frame: The decoded frame to check.
        output: The stream whose dimensions the frame must match.
        frame_bytes: The largest decoded frame to accept, in bytes.

    Raises:
        SourceError: When the frame fails a check.

    """
    if (
        (frame.width, frame.height) != (output.width, output.height)
        or not MIN_FRAME_DIMENSION <= frame.width <= MAX_FRAME_DIMENSION
        or not MIN_FRAME_DIMENSION <= frame.height <= MAX_FRAME_DIMENSION
        or frame.width % 2
        or frame.height % 2
        or frame.width * frame.height * RGB_CHANNELS > frame_bytes
        or any(component.bits > MAX_COMPONENT_BITS for component in frame.format.components)
    ):
        message = 'frame_size'
        raise SourceError(message)


def source_frames(reader: InputContainer, settings: SourceSettings) -> Iterator[tuple[av.VideoFrame, Fraction]]:
    """Select source frames with strictly increasing timestamps.

    Args:
        reader: The open source file.
        settings: The settings that hold the selected interval.

    Yields:
        Each selected frame with its source time.

    Raises:
        SourceError: When a timestamp is missing or does not increase.

    """
    previous_time: Fraction | None = None
    origin: Fraction | None = None
    for frame in reader.decode(reader.streams.video[0]):
        if frame.pts is None or frame.time_base is None:
            message = 'source_time_missing'
            raise SourceError(message)
        current = frame.pts * frame.time_base
        if origin is None:
            origin = current
        if previous_time is not None and current <= previous_time:
            message = 'timestamps'
            raise SourceError(message)
        previous_time = current
        relative = float(current - origin)
        if relative < settings.start_seconds:
            continue
        if relative >= settings.start_seconds + settings.duration_seconds:
            break
        yield frame, current


def copy_frames(
    reader: InputContainer,
    output: VideoStream,
    writer: OutputContainer,
    settings: SourceSettings,
) -> int:
    """Copy the chosen source interval while preserving usable frame timestamps.

    Args:
        reader: The open source file to decode.
        output: The stream that encodes the frames.
        writer: The output file that receives the packets.
        settings: The interval and limits of the copy.

    Returns:
        The number of frames written.

    Raises:
        SourceError: When the frame count or the file size is out of range.

    """
    frames = 0
    first_time: Fraction | None = None
    for frame, current in source_frames(reader, settings):
        if first_time is None:
            first_time = current
            output.width, output.height = frame.width, frame.height
        validate_frame(frame, output, settings.frame_bytes)
        frame.pts = round((current - first_time) * 1_000_000)
        frame.time_base = Fraction(1, 1_000_000)
        writer.mux(output.encode(frame))  # pyright: ignore[reportUnknownMemberType] # reason: PyAV's stubs leave Packet without its stream type.
        frames += 1
        if frames > MAX_FRAME_RATE * settings.duration_seconds + 1:
            message = 'source_frame_limit'
            raise SourceError(message)
        if settings.destination.exists() and settings.destination.stat().st_size > settings.maximum_bytes:
            message = 'file_limit'
            raise SourceError(message)
    if frames < MIN_SOURCE_FRAMES:
        message = 'source_frames'
        raise SourceError(message)
    writer.mux(output.encode())  # pyright: ignore[reportUnknownMemberType] # reason: PyAV's stubs leave Packet without its stream type.
    return frames


def read_settings(arguments: list[str]) -> SourceSettings:
    """Parse the fixed worker command without accepting provider text or remote input paths.

    Args:
        arguments: The worker command line, starting with the program name.

    Returns:
        The parsed source settings.

    Raises:
        SourceError: When the argument count is wrong.

    """
    if len(arguments) != SOURCE_WORKER_ARGUMENT_COUNT:
        message = 'source_video'
        raise SourceError(message)
    return SourceSettings(
        source=Path(arguments[1]),
        destination=Path(arguments[2]),
        start_seconds=float(arguments[3]),
        duration_seconds=float(arguments[4]),
        maximum_bytes=int(arguments[5]),
        frame_bytes=int(arguments[6]),
    )


def main(arguments: list[str]) -> int:
    """Accept only local paths and non-secret preparation limits.

    Args:
        arguments: The worker command line.

    Returns:
        The exit status of the worker.

    """
    return report_ready_outcome(
        lambda: prepare(read_settings(arguments)), unknown_error_code='source_video', known=SourceError
    )
