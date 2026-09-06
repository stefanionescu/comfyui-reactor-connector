"""Encode framed RGB input in a standalone, terminable worker process."""

import json
import struct
import sys
from contextlib import AbstractContextManager
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import BinaryIO, Protocol, cast

import av
import numpy as np

FRAME_HEADER = struct.Struct("<IIq")
ENCODER_ERRORS = {
    "dimensions": "Video dimensions changed during capture.",
    "frame_size": "Video frames must have even dimensions within the capture limit.",
    "timestamps": "Video timestamps stopped increasing.",
    "file_limit": "The captured video exceeds its file limit.",
    "no_frames": "No video frames were captured.",
    "truncated": "The encoder received an incomplete frame.",
    "encoder_failed": "Video encoding failed. Check free disk space and the host's media support.",
    "source_frames": "Use a source video with at least 33 frames within the input time limit.",
    "source_video": "Use a readable local SDR video with increasing timestamps.",
    "source_streams": "Use a video file with exactly one video track.",
    "source_hdr": "The video uses HDR color. Convert it to SDR before using it.",
    "source_rate": "The video needs a frame rate from 1 to 120 frames per second.",
    "source_time_missing": "The video is missing frame timestamps.",
    "source_frame_limit": "The video exceeds 120 frames per second within the selected duration.",
    "recording_video": "The recording has unsupported video or invalid timestamps.",
    "recording_audio": "The recording needs one mono or stereo audio track with valid timestamps.",
    "recording_memory": "The recording exceeds the configured media memory limit.",
    "recording_details": "The saved video's details could not be read.",
}


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

    def encode(self, frame: av.VideoFrame | None = None) -> list[object]: ...


class VideoContainer(AbstractContextManager["VideoContainer"], Protocol):
    """The output-container operations used by the capture worker."""

    def add_stream(self, codec_name: str, rate: Fraction) -> VideoStream: ...

    def mux(self, packet: object) -> None: ...


class EncodingFailure(Exception):
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
    header = source.read(FRAME_HEADER.size)
    if not header:
        return None
    if len(header) != FRAME_HEADER.size:
        raise EncodingFailure("truncated")
    width, height, timestamp = cast(tuple[int, int, int], FRAME_HEADER.unpack(header))
    size = width * height * 3
    if not (2 <= width <= 8192 and 2 <= height <= 8192) or width % 2 or height % 2 or size > limit:
        raise EncodingFailure("frame_size")
    pixels = source.read(size)
    if len(pixels) != size:
        raise EncodingFailure("truncated")
    return width, height, timestamp, pixels


def _mux(container: VideoContainer, packets: list[object], settings: EncoderSettings) -> None:
    for packet in packets:
        container.mux(packet)
        if settings.path.stat().st_size > settings.output_bytes:
            raise EncodingFailure("file_limit")


def _encode_frames(
    source: BinaryIO, container: VideoContainer, stream: VideoStream, settings: EncoderSettings
) -> tuple[int, str]:
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
            raise EncodingFailure("dimensions")
        pts = (
            timestamp - first_timestamp
            if timestamp_mode == "sender"
            else round(frame_count * 1_000_000 / settings.fps)
        )
        if pts <= previous_pts:
            raise EncodingFailure("timestamps")
        if pts >= settings.duration_us:
            break
        array = np.frombuffer(pixels, dtype=np.uint8).reshape(height, width, 3)
        frame = av.VideoFrame.from_ndarray(array, format="rgb24")
        frame.pts, frame.time_base = pts, Fraction(1, 1_000_000)
        _mux(container, stream.encode(frame), settings)
        previous_pts = pts
        frame_count += 1
    if not frame_count:
        raise EncodingFailure("no_frames")
    _mux(container, stream.encode(), settings)
    return frame_count, timestamp_mode


def encode(source: BinaryIO, settings: EncoderSettings) -> dict[str, str | int]:
    """Write an MP4 within the recording limits and report its size, timing, or errors."""
    output = cast(VideoContainer, av.open(str(settings.path), mode="w", format="mp4"))
    with output as container:
        stream = container.add_stream("libx264", rate=Fraction(settings.fps))
        stream.pix_fmt = "yuv420p"
        stream.time_base = Fraction(1, 1_000_000)
        stream.codec_context.time_base = Fraction(1, 1_000_000)
        stream.options = {"preset": "veryfast", "crf": "18"}
        print(json.dumps({"ready": True}), flush=True)
        frames, mode = _encode_frames(source, container, stream, settings)
    if settings.path.stat().st_size > settings.output_bytes:
        raise EncodingFailure("file_limit")
    return {"frames": frames, "timestamp_mode": mode}


def main() -> int:
    """Run only as an explicitly launched worker; do not import the ComfyUI host."""
    try:
        if len(sys.argv) != 6:
            raise ValueError("Invalid worker arguments.")
        settings = EncoderSettings(Path(sys.argv[1]), *(int(value) for value in sys.argv[2:]))
        if min(settings.duration_us, settings.frame_bytes, settings.output_bytes, settings.fps) < 1:
            raise ValueError("Worker limits must be positive.")
        result = encode(sys.stdin.buffer, settings)
    except EncodingFailure as error:
        print(json.dumps({"error": str(error)}), flush=True)
        return 1
    except Exception:
        print(json.dumps({"error": "encoder_failed"}), flush=True)
        return 1
    print(json.dumps(result), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
