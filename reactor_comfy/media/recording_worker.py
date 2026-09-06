"""Use recording timestamps to keep MP4 video and WAV audio in sync."""

from __future__ import annotations

import json
import math
import sys
import wave
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import TYPE_CHECKING, cast

import av
import numpy as np
from numpy.typing import NDArray

if TYPE_CHECKING:
    from .recording_types import MediaWriter

SAMPLE_RATE = 48_000


class RecordingFailure(Exception):
    """Carry a fixed worker error code without decoder text or paths."""


@dataclass(frozen=True, slots=True)
class RecordingAudio:
    samples: NDArray[np.float32]
    layout: str


def read_audio(
    source: Path, origin: Fraction, duration_seconds: float, maximum_memory: int
) -> RecordingAudio:
    """Use media timestamps, preserve gaps, and reject overlapping audio frames."""
    with (
        source.open("rb") as file,
        av.open(file, mode="r", format="mp4", options={"protocol_whitelist": "pipe"}) as reader,
    ):
        if len(reader.streams.audio) != 1:
            raise RecordingFailure("recording_audio")
        stream = reader.streams.audio[0]
        channels = len(stream.codec_context.layout.channels)
        if channels not in (1, 2):
            raise RecordingFailure("recording_audio")
        layout = "mono" if channels == 1 else "stereo"
        count = math.ceil(duration_seconds * SAMPLE_RATE)
        if count * channels * 4 > maximum_memory // 2:
            raise RecordingFailure("recording_memory")
        samples = np.zeros((channels, count), dtype=np.float32)
        resampler = av.AudioResampler(format="fltp", layout=layout, rate=SAMPLE_RATE)
        previous_end: int | None = None
        copied = 0

        def accept(frame: av.AudioFrame) -> bool:
            nonlocal previous_end, copied
            if frame.pts is None or frame.time_base is None:
                raise RecordingFailure("recording_audio")
            start = round((frame.pts * frame.time_base - origin) * SAMPLE_RATE)
            end = start + frame.samples
            if previous_end is not None and start < previous_end:
                raise RecordingFailure("recording_audio")
            previous_end = end
            left, right = max(0, start), min(count, end)
            if left < right:
                values = frame.to_ndarray()
                if not np.isfinite(values).all():
                    raise RecordingFailure("recording_audio")
                samples[:, left:right] = values[:, left - start : right - start]
                copied += right - left
            return start >= count

        finished = False
        for frame in reader.decode(stream):
            for converted in resampler.resample(frame):
                finished = accept(converted)
                if finished:
                    break
            if finished:
                break
        if not finished:
            for converted in resampler.resample(None):
                accept(converted)
        if copied == 0:
            raise RecordingFailure("recording_audio")
        return RecordingAudio(samples, layout)


@dataclass(frozen=True, slots=True)
class RecordingVideo:
    origin: Fraction
    rate: Fraction
    width: int
    height: int


def video_info(source: Path, memory_limit: int, start_seconds: float = 0) -> RecordingVideo:
    with (
        source.open("rb") as file,
        av.open(file, mode="r", format="mp4", options={"protocol_whitelist": "pipe"}) as reader,
    ):
        if len(reader.streams.video) != 1:
            raise RecordingFailure("recording_video")
        stream = reader.streams.video[0]
        rate = stream.average_rate
        if rate is None or not 1 <= rate <= 120 or stream.codec_context.color_trc in (16, 18):
            raise RecordingFailure("recording_video")
        frames = reader.decode(stream)
        frame = next(frames, None)
        if frame is None or frame.pts is None or frame.time_base is None:
            raise RecordingFailure("recording_video")
        target = frame.pts * frame.time_base + Fraction(str(start_seconds))
        while frame.pts * frame.time_base < target:
            frame = next(frames, None)
            if frame is None or frame.pts is None or frame.time_base is None:
                raise RecordingFailure("recording_video")
        if (
            not 2 <= frame.width <= 4096
            or not 2 <= frame.height <= 4096
            or frame.width % 2
            or frame.height % 2
            or frame.width * frame.height * 3 > memory_limit
        ):
            raise RecordingFailure("recording_memory")
        return RecordingVideo(frame.pts * frame.time_base, rate, frame.width, frame.height)


class AudioEncoder:
    """Interleave timestamped audio while video advances, then finish its exact interval."""

    def __init__(self, writer: MediaWriter, audio: RecordingAudio) -> None:
        self.writer = writer
        self.audio = audio
        self.position = 0
        self.stream = writer.add_stream("aac", rate=SAMPLE_RATE)
        self.stream.layout = audio.layout
        self.stream.time_base = Fraction(1, SAMPLE_RATE)

    def through(self, samples: int) -> None:
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

    def finish(self) -> None:
        for packet in self.stream.encode(None):
            self.writer.mux(packet)


def encode_video(
    source: Path,
    destination: Path,
    audio: RecordingAudio,
    info: RecordingVideo,
    duration_seconds: float,
    maximum_bytes: int,
) -> tuple[int, int]:
    frames = 0
    previous: Fraction | None = None
    with (
        source.open("rb") as file,
        av.open(file, mode="r", format="mp4", options={"protocol_whitelist": "pipe"}) as reader,
        cast("MediaWriter", av.open(str(destination), mode="w", format="mp4")) as writer,
    ):
        video = writer.add_stream("libx264", rate=info.rate)
        video.width, video.height = info.width, info.height
        video.pix_fmt = "yuv420p"
        video.time_base = Fraction(1, 1_000_000)
        video.codec_context.time_base = video.time_base
        video.options = {"preset": "veryfast", "crf": "18"}
        sound = AudioEncoder(writer, audio)
        for frame in reader.decode(video=0):
            if frame.pts is None or frame.time_base is None:
                raise RecordingFailure("recording_video")
            current = frame.pts * frame.time_base - info.origin
            if current < 0:
                continue
            if previous is not None and current <= previous:
                raise RecordingFailure("recording_video")
            current_us = round(current * 1_000_000)
            if current_us >= round(duration_seconds * 1_000_000):
                break
            if (frame.width, frame.height) != (info.width, info.height):
                raise RecordingFailure("dimensions")
            if any(component.bits > 8 for component in frame.format.components):
                raise RecordingFailure("recording_video")
            frame.pts, frame.time_base = current_us, Fraction(1, 1_000_000)
            for packet in video.encode(frame):
                writer.mux(packet)
            sound.through(round(current * SAMPLE_RATE))
            previous = current
            frames += 1
            if frames > 120 * duration_seconds + 1:
                raise RecordingFailure("recording_video")
            if destination.exists() and destination.stat().st_size > maximum_bytes:
                raise RecordingFailure("file_limit")
        if previous is None:
            raise RecordingFailure("recording_video")
        count = round(min(duration_seconds, float(previous + 1 / info.rate)) * SAMPLE_RATE)
        sound.through(count)
        sound.finish()
        for packet in video.encode(None):
            writer.mux(packet)
    if destination.stat().st_size > maximum_bytes:
        raise RecordingFailure("file_limit")
    return frames, count


def write_wav(path: Path, audio: RecordingAudio, count: int, maximum_bytes: int) -> None:
    if count * audio.samples.shape[0] * 2 + 44 > maximum_bytes:
        raise RecordingFailure("file_limit")
    with wave.open(str(path), "wb") as output:
        output.setnchannels(audio.samples.shape[0])
        output.setsampwidth(2)
        output.setframerate(SAMPLE_RATE)
        for start in range(0, count, 4096):
            chunk = audio.samples[:, start : min(count, start + 4096)]
            pcm = np.rint(np.clip(chunk, -1, 1) * 32767).astype("<i2")
            output.writeframes(pcm.T.tobytes())


def prepare(
    source: Path,
    destination: Path,
    wav: Path,
    duration: float,
    size_limit: int,
    memory_limit: int,
    start_seconds: float = 0,
) -> dict[str, str | int]:
    if not math.isfinite(start_seconds) or not 0 <= start_seconds <= 3600:
        raise RecordingFailure("recording_video")
    info = video_info(source, memory_limit, start_seconds)
    audio = read_audio(source, info.origin, duration, memory_limit - info.width * info.height * 3)
    frames, count = encode_video(source, destination, audio, info, duration, size_limit)
    write_wav(wav, audio, count, size_limit)
    return {
        "frames": frames,
        "timestamp_mode": "recording_pts",
        "audio_samples": count,
        "sample_rate": SAMPLE_RATE,
        "channels": audio.samples.shape[0],
    }


def main() -> int:
    print(json.dumps({"ready": True}), flush=True)
    try:
        if len(sys.argv) != 8:
            raise RecordingFailure("recording_video")
        result = prepare(
            Path(sys.argv[1]),
            Path(sys.argv[2]),
            Path(sys.argv[3]),
            float(sys.argv[4]),
            int(sys.argv[5]),
            int(sys.argv[6]),
            float(sys.argv[7]),
        )
    except RecordingFailure as error:
        print(json.dumps({"error": str(error)}), flush=True)
        return 1
    except Exception:
        print(json.dumps({"error": "recording_video"}), flush=True)
        return 1
    print(json.dumps(result), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
