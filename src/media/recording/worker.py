"""Use recording timestamps to keep MP4 video and WAV audio in sync."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING
from pathlib import Path
from fractions import Fraction

import av

from src.state.recording import RecordingVideo, RecordingSettings

from .audio import AudioEncoder, RecordingAudio, write_wav, read_audio
from ..protocol import report_ready_outcome
from ...config.media.audio import (
    SAMPLE_RATE,
)
from ...config.media.video import (
    ENCODER_CRF,
    ENCODER_NAME,
    ENCODER_PRESET,
    MAX_FRAME_RATE,
    MAX_START_SECONDS,
    HDR_TRANSFER_CODES,
    MAX_COMPONENT_BITS,
    MAX_FRAME_DIMENSION,
    MIN_FRAME_DIMENSION,
    ENCODER_PIXEL_FORMAT,
)
from ...config.media.images import RGB_CHANNELS

if TYPE_CHECKING:
    from collections.abc import Iterator

    from av.container.input import InputContainer


WORKER_ARGUMENT_COUNT = 8


def video_timing(source: Path, memory_limit: int, start_seconds: float = 0) -> RecordingVideo:
    """Find the first selected frame and validate recording rate, color, dimensions, and memory.

    Args:
        source: The recording file to inspect.
        memory_limit: The largest decoded frame to accept, in bytes.
        start_seconds: The offset of the interval from the first frame.

    Returns:
        The origin, rate, width, and height of the selected video.

    Raises:
        ValueError: When the video is missing, unsupported, or too large.

    """
    with (
        source.open('rb') as file,
        av.open(file, mode='r', format='mp4', options={'protocol_whitelist': 'pipe'}) as reader,
    ):
        if len(reader.streams.video) != 1:
            message = 'recording_video'
            raise ValueError(message)
        stream = reader.streams.video[0]
        rate = stream.average_rate
        if rate is None or not 1 <= rate <= MAX_FRAME_RATE or stream.codec_context.color_trc in HDR_TRANSFER_CODES:
            message = 'recording_video'
            raise ValueError(message)
        frames = reader.decode(stream)
        frame = next(frames, None)
        if frame is None or frame.pts is None or frame.time_base is None:
            message = 'recording_video'
            raise ValueError(message)
        target = frame.pts * frame.time_base + Fraction(str(start_seconds))
        while frame.pts * frame.time_base < target:
            frame = next(frames, None)
            if frame is None or frame.pts is None or frame.time_base is None:
                message = 'recording_video'
                raise ValueError(message)
        if (
            not MIN_FRAME_DIMENSION <= frame.width <= MAX_FRAME_DIMENSION
            or not MIN_FRAME_DIMENSION <= frame.height <= MAX_FRAME_DIMENSION
            or frame.width % 2
            or frame.height % 2
            or frame.width * frame.height * RGB_CHANNELS > memory_limit
        ):
            message = 'recording_memory'
            raise ValueError(message)
        return RecordingVideo(frame.pts * frame.time_base, rate, frame.width, frame.height)


def recording_frames(
    reader: InputContainer, timing: RecordingVideo, duration_seconds: float
) -> Iterator[tuple[av.VideoFrame, Fraction]]:
    """Yield selected standard dynamic range (SDR) frames, with timestamps that increase from the recording origin.

    Args:
        reader: The open recording.
        timing: The origin and dimensions of the selected video.
        duration_seconds: The length of the interval to yield.

    Yields:
        Each frame with its time from the origin.

    Raises:
        ValueError: When a frame has no timestamp, repeats a time, changes size, or has too many bits.

    """
    previous: Fraction | None = None
    for frame in reader.decode(video=0):
        if frame.pts is None or frame.time_base is None:
            message = 'recording_video'
            raise ValueError(message)
        current = frame.pts * frame.time_base - timing.origin
        if current < 0:
            continue
        if previous is not None and current <= previous:
            message = 'recording_video'
            raise ValueError(message)
        current_us = round(current * 1_000_000)
        if current_us >= round(duration_seconds * 1_000_000):
            break
        if (frame.width, frame.height) != (timing.width, timing.height):
            message = 'dimensions'
            raise ValueError(message)
        if any(component.bits > MAX_COMPONENT_BITS for component in frame.format.components):
            message = 'recording_video'
            raise ValueError(message)
        frame.pts, frame.time_base = current_us, Fraction(1, 1_000_000)
        previous = current
        yield frame, current


def encode_video(settings: RecordingSettings, audio: RecordingAudio, timing: RecordingVideo) -> tuple[int, int]:
    """Encode the selected video interval and matching audio within the output size limit.

    Args:
        settings: The paths, duration, and limits of the worker.
        audio: The samples to encode beside the video.
        timing: The origin, rate, and dimensions of the video.

    Returns:
        The frame count and the audio sample count.

    Raises:
        ValueError: When no frame is selected, or a frame or size limit is passed.

    """
    frames = 0
    previous: Fraction | None = None
    with (
        settings.source.open('rb') as file,
        av.open(file, mode='r', format='mp4', options={'protocol_whitelist': 'pipe'}) as reader,
        av.open(str(settings.destination), mode='w', format='mp4') as writer,
    ):
        video = writer.add_stream(ENCODER_NAME, rate=timing.rate, pix_fmt=ENCODER_PIXEL_FORMAT)  # pyright: ignore[reportUnknownMemberType] # reason: PyAV's stubs leave Packet without its stream type.
        video.width, video.height = timing.width, timing.height
        video.time_base = Fraction(1, 1_000_000)
        video.codec_context.time_base = video.time_base
        video.options = {'preset': ENCODER_PRESET, 'crf': ENCODER_CRF}
        sound = AudioEncoder(writer, audio)
        for frame, current in recording_frames(reader, timing, settings.duration_seconds):
            writer.mux(video.encode(frame))  # pyright: ignore[reportUnknownMemberType] # reason: PyAV's stubs leave Packet without its stream type.
            sound.encode_until(round(current * SAMPLE_RATE))
            previous = current
            frames += 1
            if frames > MAX_FRAME_RATE * settings.duration_seconds + 1:
                message = 'recording_video'
                raise ValueError(message)
            if settings.destination.exists() and settings.destination.stat().st_size > settings.max_output_bytes:
                message = 'file_limit'
                raise ValueError(message)
        if previous is None:
            message = 'recording_video'
            raise ValueError(message)
        count = round(min(settings.duration_seconds, float(previous + 1 / timing.rate)) * SAMPLE_RATE)
        # Encode the remaining selected samples, then flush all audio packets into the recording.
        sound.encode_until(count)
        writer.mux(sound.stream.encode(None))  # pyright: ignore[reportUnknownMemberType] # reason: PyAV's stubs leave Packet without its stream type.
        writer.mux(video.encode(None))  # pyright: ignore[reportUnknownMemberType] # reason: PyAV's stubs leave Packet without its stream type.
    if settings.destination.stat().st_size > settings.max_output_bytes:
        message = 'file_limit'
        raise ValueError(message)
    return frames, count


def prepare(settings: RecordingSettings) -> dict[str, str | int]:
    """Select the recording interval and produce synchronized MP4 and WAV outputs.

    Args:
        settings: The paths, interval, and limits of the worker.

    Returns:
        The frame count, timestamp mode, and audio facts of the outputs.

    Raises:
        ValueError: When the start offset is out of range.

    """
    if not math.isfinite(settings.start_seconds) or not 0 <= settings.start_seconds <= MAX_START_SECONDS:
        message = 'recording_video'
        raise ValueError(message)
    timing = video_timing(settings.source, settings.max_memory_bytes, settings.start_seconds)
    audio = read_audio(
        settings.source,
        timing.origin,
        settings.duration_seconds,
        settings.max_memory_bytes - timing.width * timing.height * RGB_CHANNELS,
    )
    frames, count = encode_video(settings, audio, timing)
    write_wav(settings.wav, audio, count, settings.max_output_bytes)
    return {
        'frames': frames,
        'timestamp_mode': 'recording_pts',
        'audio_samples': count,
        'sample_rate': SAMPLE_RATE,
        'channels': audio.samples.shape[0],
    }


def read_settings(arguments: list[str]) -> RecordingSettings:
    """Parse the fixed recording worker command without exposing its local paths.

    Args:
        arguments: The command line of the recording worker, with the program name first.

    Returns:
        The parsed recording settings.

    Raises:
        ValueError: When the argument count is wrong.

    """
    if len(arguments) != WORKER_ARGUMENT_COUNT:
        message = 'recording_video'
        raise ValueError(message)
    return RecordingSettings(
        source=Path(arguments[1]),
        destination=Path(arguments[2]),
        wav=Path(arguments[3]),
        duration_seconds=float(arguments[4]),
        max_output_bytes=int(arguments[5]),
        max_memory_bytes=int(arguments[6]),
        start_seconds=float(arguments[7]),
    )


def main(arguments: list[str]) -> int:
    """Report readiness and return recording facts or fixed error codes without native error text.

    Args:
        arguments: The command line of the recording worker.

    Returns:
        The exit status of the worker.

    """
    return report_ready_outcome(
        lambda: prepare(read_settings(arguments)),
        unknown_error_code='recording_video',
        known=ValueError,
        allowed_codes=frozenset({'recording_audio', 'recording_memory', 'recording_video', 'dimensions', 'file_limit'}),
    )
