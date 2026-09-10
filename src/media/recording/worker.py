"""Use recording timestamps to keep MP4 video and WAV audio in sync."""

from __future__ import annotations

import av
import sys
import json
import math
import wave
import numpy as np
from pathlib import Path
from itertools import chain
from fractions import Fraction
from dataclasses import dataclass
from typing import cast, TYPE_CHECKING
from config.media.audio import MAX_CHANNELS, MIN_CHANNELS, SAMPLE_RATE
from config.media.video import (
    ENCODER_CRF,
    ENCODER_NAME,
    ENCODER_PRESET,
    MAX_FRAME_RATE,
    MAX_START_SECONDS,
    MAX_COMPONENT_BITS,
    MAX_FRAME_DIMENSION,
    MIN_FRAME_DIMENSION,
    ENCODER_PIXEL_FORMAT,
)

if TYPE_CHECKING:
    from .streams import MediaWriter
    from numpy.typing import NDArray
    from collections.abc import Iterator
    from av.container.input import InputContainer


WORKER_ARGUMENT_COUNT = 8


@dataclass(frozen=True, slots=True)
class RecordingAudio:
    """Normalized audio samples and their mono or stereo channel layout."""

    samples: NDArray[np.float32]
    layout: str


@dataclass(frozen=True, slots=True)
class RecordingVideo:
    """The recording origin, frame rate, and dimensions used for conversion."""

    origin: Fraction
    rate: Fraction
    width: int
    height: int


class AudioEncoder:
    """Interleave timestamped audio while video advances, then finish its exact interval."""

    def __init__(self, writer: MediaWriter, audio: RecordingAudio) -> None:
        """Configure an AAC stream on the shared recording sample clock."""
        self.writer = writer
        self.audio = audio
        self.position = 0
        self.stream = writer.add_stream("aac", rate=SAMPLE_RATE)
        self.stream.layout = audio.layout
        self.stream.time_base = Fraction(1, SAMPLE_RATE)

    def through(self, samples: int) -> None:
        """Encode audio up to the requested sample position in small consecutive blocks."""
        end = min(samples, self.audio.samples.shape[1])
        while self.position < end:
            stop = min(end, self.position + 1024)
            values = np.ascontiguousarray(self.audio.samples[:, self.position : stop])
            frame = av.AudioFrame.from_ndarray(values, format="fltp", layout=self.audio.layout)
            frame.sample_rate = SAMPLE_RATE
            frame.time_base = Fraction(1, SAMPLE_RATE)
            frame.pts = self.position
            for packet in self.stream.encode(frame):
                self.writer.mux(packet)
            self.position = stop

    def finish(self, samples: int) -> None:
        """Encode the remaining selected samples and flush all audio packets into the recording."""
        self.through(samples)
        for packet in self.stream.encode(None):
            self.writer.mux(packet)


@dataclass(frozen=True, slots=True)
class RecordingSettings:
    """Local recording paths, selected interval, and output and memory limits."""

    source: Path
    destination: Path
    wav: Path
    duration: float
    size_limit: int
    memory_limit: int
    start_seconds: float


def copy_audio_frame(
    frame: av.AudioFrame,
    samples: NDArray[np.float32],
    origin: Fraction,
    previous_end: int | None,
) -> tuple[int, int, bool]:
    """Copy nonoverlapping audio and return its end, copied sample count, and interval completion."""
    if frame.pts is None or frame.time_base is None:
        msg = "recording_audio"
        raise ValueError(msg)
    start = round((frame.pts * frame.time_base - origin) * SAMPLE_RATE)
    end = start + frame.samples
    if previous_end is not None and start < previous_end:
        msg = "recording_audio"
        raise ValueError(msg)
    count = samples.shape[1]
    left, right = max(0, start), min(count, end)
    copied = 0
    if left < right:
        values = frame.to_ndarray()
        if not np.isfinite(values).all():
            msg = "recording_audio"
            raise ValueError(msg)
        samples[:, left:right] = values[:, left - start : right - start]
        copied = right - left
    return end, copied, start >= count


def read_audio(source: Path, origin: Fraction, duration_seconds: float, maximum_memory: int) -> RecordingAudio:
    """Use media timestamps, preserve gaps, and reject overlapping audio frames."""
    with (
        source.open("rb") as file,
        av.open(file, mode="r", format="mp4", options={"protocol_whitelist": "pipe"}) as reader,
    ):
        if len(reader.streams.audio) != 1:
            msg = "recording_audio"
            raise ValueError(msg)
        stream = reader.streams.audio[0]
        channels = len(stream.codec_context.layout.channels)
        if not MIN_CHANNELS <= channels <= MAX_CHANNELS:
            msg = "recording_audio"
            raise ValueError(msg)
        layout = "mono" if channels == 1 else "stereo"
        count = math.ceil(duration_seconds * SAMPLE_RATE)
        if count * channels * 4 > maximum_memory // 2:
            msg = "recording_memory"
            raise ValueError(msg)
        samples = np.zeros((channels, count), dtype=np.float32)
        resampler = av.AudioResampler(format="fltp", layout=layout, rate=SAMPLE_RATE)
        previous_end: int | None = None
        copied = 0

        converted = chain.from_iterable(resampler.resample(frame) for frame in chain(reader.decode(stream), (None,)))
        for frame in converted:
            previous_end, accepted, finished = copy_audio_frame(frame, samples, origin, previous_end)
            copied += accepted
            if finished:
                break
        if copied == 0:
            msg = "recording_audio"
            raise ValueError(msg)
        return RecordingAudio(samples, layout)


def video_timing(source: Path, memory_limit: int, start_seconds: float = 0) -> RecordingVideo:
    """Find the first selected frame and validate recording rate, color, dimensions, and memory."""
    with (
        source.open("rb") as file,
        av.open(file, mode="r", format="mp4", options={"protocol_whitelist": "pipe"}) as reader,
    ):
        if len(reader.streams.video) != 1:
            msg = "recording_video"
            raise ValueError(msg)
        stream = reader.streams.video[0]
        rate = stream.average_rate
        if rate is None or not 1 <= rate <= MAX_FRAME_RATE or stream.codec_context.color_trc in (16, 18):
            msg = "recording_video"
            raise ValueError(msg)
        frames = reader.decode(stream)
        frame = next(frames, None)
        if frame is None or frame.pts is None or frame.time_base is None:
            msg = "recording_video"
            raise ValueError(msg)
        target = frame.pts * frame.time_base + Fraction(str(start_seconds))
        while frame.pts * frame.time_base < target:
            frame = next(frames, None)
            if frame is None or frame.pts is None or frame.time_base is None:
                msg = "recording_video"
                raise ValueError(msg)
        if (
            not MIN_FRAME_DIMENSION <= frame.width <= MAX_FRAME_DIMENSION
            or not MIN_FRAME_DIMENSION <= frame.height <= MAX_FRAME_DIMENSION
            or frame.width % 2
            or frame.height % 2
            or frame.width * frame.height * 3 > memory_limit
        ):
            msg = "recording_memory"
            raise ValueError(msg)
        return RecordingVideo(frame.pts * frame.time_base, rate, frame.width, frame.height)


def recording_frames(
    reader: InputContainer, timing: RecordingVideo, duration_seconds: float
) -> Iterator[tuple[av.VideoFrame, Fraction]]:
    """Yield selected SDR frames with increasing timestamps relative to the recording origin."""
    previous: Fraction | None = None
    for frame in reader.decode(video=0):
        if frame.pts is None or frame.time_base is None:
            msg = "recording_video"
            raise ValueError(msg)
        current = frame.pts * frame.time_base - timing.origin
        if current < 0:
            continue
        if previous is not None and current <= previous:
            msg = "recording_video"
            raise ValueError(msg)
        current_us = round(current * 1_000_000)
        if current_us >= round(duration_seconds * 1_000_000):
            break
        if (frame.width, frame.height) != (timing.width, timing.height):
            msg = "dimensions"
            raise ValueError(msg)
        if any(component.bits > MAX_COMPONENT_BITS for component in frame.format.components):
            msg = "recording_video"
            raise ValueError(msg)
        frame.pts, frame.time_base = current_us, Fraction(1, 1_000_000)
        previous = current
        yield frame, current


def encode_video(settings: RecordingSettings, audio: RecordingAudio, timing: RecordingVideo) -> tuple[int, int]:
    """Encode the selected video interval and matching audio within the output size limit."""
    frames = 0
    previous: Fraction | None = None
    with (
        settings.source.open("rb") as file,
        av.open(file, mode="r", format="mp4", options={"protocol_whitelist": "pipe"}) as reader,
        cast("MediaWriter", av.open(str(settings.destination), mode="w", format="mp4")) as writer,
    ):
        video = writer.add_stream(ENCODER_NAME, rate=timing.rate)
        video.width, video.height = timing.width, timing.height
        video.pix_fmt = ENCODER_PIXEL_FORMAT
        video.time_base = Fraction(1, 1_000_000)
        video.codec_context.time_base = video.time_base
        video.options = {"preset": ENCODER_PRESET, "crf": ENCODER_CRF}
        sound = AudioEncoder(writer, audio)
        for frame, current in recording_frames(reader, timing, settings.duration):
            for packet in video.encode(frame):
                writer.mux(packet)
            sound.through(round(current * SAMPLE_RATE))
            previous = current
            frames += 1
            if frames > MAX_FRAME_RATE * settings.duration + 1:
                msg = "recording_video"
                raise ValueError(msg)
            if settings.destination.exists() and settings.destination.stat().st_size > settings.size_limit:
                msg = "file_limit"
                raise ValueError(msg)
        if previous is None:
            msg = "recording_video"
            raise ValueError(msg)
        count = round(min(settings.duration, float(previous + 1 / timing.rate)) * SAMPLE_RATE)
        sound.finish(count)
        for packet in video.encode(None):
            writer.mux(packet)
    if settings.destination.stat().st_size > settings.size_limit:
        msg = "file_limit"
        raise ValueError(msg)
    return frames, count


def write_wav(path: Path, audio: RecordingAudio, count: int, maximum_bytes: int) -> None:
    """Write the selected samples as size-limited signed 16-bit PCM audio."""
    if count * audio.samples.shape[0] * 2 + 44 > maximum_bytes:
        msg = "file_limit"
        raise ValueError(msg)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(audio.samples.shape[0])
        output.setsampwidth(2)
        output.setframerate(SAMPLE_RATE)
        for start in range(0, count, 4096):
            chunk = audio.samples[:, start : min(count, start + 4096)]
            pcm = np.rint(np.clip(chunk, -1, 1) * 32767).astype("<i2")
            output.writeframes(pcm.T.tobytes())


def prepare(settings: RecordingSettings) -> dict[str, str | int]:
    """Select the recording interval and produce synchronized MP4 and WAV outputs."""
    if not math.isfinite(settings.start_seconds) or not 0 <= settings.start_seconds <= MAX_START_SECONDS:
        msg = "recording_video"
        raise ValueError(msg)
    timing = video_timing(settings.source, settings.memory_limit, settings.start_seconds)
    audio = read_audio(
        settings.source, timing.origin, settings.duration, settings.memory_limit - timing.width * timing.height * 3
    )
    frames, count = encode_video(settings, audio, timing)
    write_wav(settings.wav, audio, count, settings.size_limit)
    return {
        "frames": frames,
        "timestamp_mode": "recording_pts",
        "audio_samples": count,
        "sample_rate": SAMPLE_RATE,
        "channels": audio.samples.shape[0],
    }


def read_settings(arguments: list[str]) -> RecordingSettings:
    """Parse the fixed recording worker command without exposing its local paths."""
    if len(arguments) != WORKER_ARGUMENT_COUNT:
        msg = "recording_video"
        raise ValueError(msg)
    return RecordingSettings(
        source=Path(arguments[1]),
        destination=Path(arguments[2]),
        wav=Path(arguments[3]),
        duration=float(arguments[4]),
        size_limit=int(arguments[5]),
        memory_limit=int(arguments[6]),
        start_seconds=float(arguments[7]),
    )


def main(arguments: list[str]) -> int:
    """Report readiness and return recording facts or fixed error codes without native error text."""
    sys.stdout.write(str(json.dumps({"ready": True})) + "\n")
    sys.stdout.flush()
    try:
        result = prepare(read_settings(arguments))
    except ValueError as error:
        code = str(error)
        if code not in {
            "recording_audio",
            "recording_memory",
            "recording_video",
            "dimensions",
            "file_limit",
        }:
            code = "recording_video"
        sys.stdout.write(str(json.dumps({"error": code})) + "\n")
        sys.stdout.flush()
        return 1
    except Exception:  # noqa: BLE001 -- reason: The worker protocol permits only fixed error codes, never native exception text.
        sys.stdout.write(str(json.dumps({"error": "recording_video"})) + "\n")
        sys.stdout.flush()
        return 1
    sys.stdout.write(str(json.dumps(result)) + "\n")
    sys.stdout.flush()
    return 0
