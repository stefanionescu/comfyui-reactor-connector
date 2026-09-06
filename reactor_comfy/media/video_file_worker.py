"""Prepare local video incrementally in a process the host can terminate."""

import json
import sys
from contextlib import AbstractContextManager
from fractions import Fraction
from pathlib import Path
from typing import Protocol, cast

import av


class VideoStream(Protocol):
    width: int
    height: int
    pix_fmt: str
    time_base: Fraction
    options: dict[str, str]
    codec_context: av.VideoCodecContext

    def encode(self, frame: av.VideoFrame | None = None) -> list[object]: ...


class VideoContainer(AbstractContextManager["VideoContainer"], Protocol):
    def add_stream(self, codec_name: str, rate: Fraction) -> VideoStream: ...

    def mux(self, packet: object) -> None: ...


class SourceFailure(Exception):
    """Report a fixed code without exposing input paths or decoder messages."""


def prepare(
    source: Path,
    destination: Path,
    start_seconds: float,
    duration_seconds: float,
    maximum_bytes: int,
    frame_bytes: int,
    *,
    browser_recording: bool = False,
) -> dict[str, int | str]:
    """Write a video-only MP4, preserving source timing inside the selected interval."""
    frames = 0
    first_time: Fraction | None = None
    previous_time: Fraction | None = None
    origin: Fraction | None = None
    # A file handle prevents an input string from being interpreted as a URL.
    # Restrict demuxers and protocols so playlists cannot fetch other resources.
    with (
        source.open("rb") as file,
        av.open(
            file,
            mode="r",
            options={
                "format_whitelist": "matroska,webm"
                if browser_recording
                else "mov,matroska,webm,avi",
                "protocol_whitelist": "pipe",
            },
        ) as reader,
        cast(VideoContainer, av.open(str(destination), "w", format="mp4")) as writer,
    ):
        if len(reader.streams.video) != 1:
            raise SourceFailure("source_streams")
        input_stream = reader.streams.video[0]
        if browser_recording and (
            len(reader.streams) != 1 or input_stream.codec_context.name not in ("vp8", "vp9")
        ):
            raise SourceFailure("recording_video")
        if input_stream.codec_context.color_trc in (16, 18):
            raise SourceFailure("source_hdr")
        rate = input_stream.average_rate
        if browser_recording and rate is None:
            # WebM from MediaRecorder may omit a frame rate. This rate initializes
            # the encoder; each source timestamp below still sets when its frame appears.
            rate = Fraction(30)
        if rate is None or not 1 <= rate <= 120:
            raise SourceFailure("source_rate")
        output = writer.add_stream("libx264", rate=rate)
        output.pix_fmt = "yuv420p"
        output.time_base = Fraction(1, 1_000_000)
        output.codec_context.time_base = output.time_base
        output.options = {"preset": "veryfast", "crf": "18"}
        for frame in reader.decode(input_stream):
            if frame.pts is None or frame.time_base is None:
                raise SourceFailure("source_time_missing")
            current = frame.pts * frame.time_base
            if origin is None:
                origin = current
            if previous_time is not None:
                if current < previous_time or (current == previous_time and not browser_recording):
                    raise SourceFailure("timestamps")
                if current == previous_time:
                    # MediaRecorder can assign the same millisecond to several frames.
                    # Keep one frame without moving later frames on the timeline.
                    continue
            previous_time = current
            relative = float(current - origin)
            if relative < start_seconds:
                continue
            if relative >= start_seconds + duration_seconds:
                break
            if first_time is None:
                first_time = current
                output.width, output.height = frame.width, frame.height
            if (
                (frame.width, frame.height) != (output.width, output.height)
                or not 2 <= frame.width <= 4096
                or not 2 <= frame.height <= 4096
                or frame.width % 2
                or frame.height % 2
                or frame.width * frame.height * 3 > frame_bytes
                or any(component.bits > 8 for component in frame.format.components)
            ):
                raise SourceFailure("frame_size")
            frame.pts = round((current - first_time) * 1_000_000)
            frame.time_base = Fraction(1, 1_000_000)
            for packet in output.encode(frame):
                writer.mux(packet)
            frames += 1
            if frames > 120 * duration_seconds + 1:
                raise SourceFailure("source_frame_limit")
            if destination.exists() and destination.stat().st_size > maximum_bytes:
                raise SourceFailure("file_limit")
        if frames < (1 if browser_recording else 33):
            raise SourceFailure("no_frames" if browser_recording else "source_frames")
        for packet in output.encode():
            writer.mux(packet)
    if destination.stat().st_size > maximum_bytes:
        raise SourceFailure("file_limit")
    return {"frames": frames, "timestamp_mode": "sender"}


def main() -> int:
    """Accept only local paths and non-secret preparation limits."""
    print(json.dumps({"ready": True}), flush=True)
    try:
        if len(sys.argv) not in (7, 8) or (len(sys.argv) == 8 and sys.argv[7] != "browser"):
            raise SourceFailure("source_video")
        result = prepare(
            Path(sys.argv[1]),
            Path(sys.argv[2]),
            float(sys.argv[3]),
            float(sys.argv[4]),
            int(sys.argv[5]),
            int(sys.argv[6]),
            browser_recording=len(sys.argv) == 8,
        )
    except SourceFailure as error:
        print(json.dumps({"error": str(error)}), flush=True)
        return 1
    except Exception:
        print(json.dumps({"error": "source_video"}), flush=True)
        return 1
    print(json.dumps(result), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
