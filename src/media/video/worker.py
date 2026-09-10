"""Prepare local video incrementally in a process the host can terminate."""

import av
import sys
import json
from pathlib import Path
from fractions import Fraction
from types import TracebackType
from dataclasses import dataclass
from collections.abc import Iterator
from typing import Self, cast, Protocol
from av.container.input import InputContainer
from config.media.video import MAX_FRAME_RATE, MAX_COMPONENT_BITS, MAX_FRAME_DIMENSION, MIN_FRAME_DIMENSION


BROWSER_WORKER_ARGUMENT_COUNT = 8


class VideoStream(Protocol):
    """Video encoder fields and packet operations used by the local media worker."""

    width: int
    height: int
    pix_fmt: str
    time_base: Fraction
    options: dict[str, str]
    codec_context: av.VideoCodecContext

    def encode(self, frame: av.VideoFrame | None = None) -> list[object]:
        """Encode one video frame, or flush pending packets when the frame is None."""
        raise NotImplementedError


class VideoContainer(Protocol):
    """Container operations used to create and write an encoded video track."""

    def __enter__(self) -> Self:
        """Return the open video container."""
        raise NotImplementedError

    def __exit__(
        self,
        _exception_type: type[BaseException] | None,
        _exception: BaseException | None,
        _traceback: TracebackType | None,
    ) -> bool | None:
        """Close the container when its context ends."""
        raise NotImplementedError

    def add_stream(self, _codec_name: str, /, rate: Fraction) -> VideoStream:
        """Create an encoder for the selected video codec and frame rate."""
        raise NotImplementedError

    def mux(self, packet: object) -> None:
        """Write an encoded packet into the output container."""
        raise NotImplementedError


class SourceError(Exception):
    """Report a fixed code without exposing input paths or decoder messages."""


@dataclass(frozen=True, slots=True)
class SourceSettings:
    """Local source paths, selected time interval, and limits for one preparation worker."""

    source: Path
    destination: Path
    start_seconds: float
    duration_seconds: float
    maximum_bytes: int
    frame_bytes: int
    browser_recording: bool


def prepare(settings: SourceSettings) -> dict[str, int | str]:
    """Write a video-only MP4, preserving source timing inside the selected interval."""
    # A file handle prevents an input string from being interpreted as a URL.
    # Restrict demuxers and protocols so playlists cannot fetch other resources.
    with (
        settings.source.open("rb") as file,
        av.open(
            file,
            mode="r",
            options={
                "format_whitelist": "matroska,webm" if settings.browser_recording else "mov,matroska,webm,avi",
                "protocol_whitelist": "pipe",
            },
        ) as reader,
        cast("VideoContainer", av.open(str(settings.destination), "w", format="mp4")) as writer,
    ):
        if len(reader.streams.video) != 1:
            msg = "source_streams"
            raise SourceError(msg)
        input_stream = reader.streams.video[0]
        if settings.browser_recording and (
            len(reader.streams) != 1 or input_stream.codec_context.name not in ("vp8", "vp9")
        ):
            msg = "recording_video"
            raise SourceError(msg)
        if input_stream.codec_context.color_trc in (16, 18):
            msg = "source_hdr"
            raise SourceError(msg)
        rate = input_stream.average_rate
        if settings.browser_recording and rate is None:
            # WebM from MediaRecorder may omit a frame rate. This rate initializes
            # the encoder; each source timestamp below still sets when its frame appears.
            rate = Fraction(30)
        if rate is None or not 1 <= rate <= MAX_FRAME_RATE:
            msg = "source_rate"
            raise SourceError(msg)
        output = writer.add_stream("libx264", rate=rate)
        output.pix_fmt = "yuv420p"
        output.time_base = Fraction(1, 1_000_000)
        output.codec_context.time_base = output.time_base
        output.options = {"preset": "veryfast", "crf": "18"}
        frames = copy_frames(reader, output, writer, settings)

    if settings.destination.stat().st_size > settings.maximum_bytes:
        msg = "file_limit"
        raise SourceError(msg)
    return {"frames": frames, "timestamp_mode": "sender"}


def validate_frame(frame: av.VideoFrame, output: VideoStream, frame_bytes: int) -> None:
    """Reject changing dimensions, oversized frames, and unsupported pixel depth."""
    if (
        (frame.width, frame.height) != (output.width, output.height)
        or not MIN_FRAME_DIMENSION <= frame.width <= MAX_FRAME_DIMENSION
        or not MIN_FRAME_DIMENSION <= frame.height <= MAX_FRAME_DIMENSION
        or frame.width % 2
        or frame.height % 2
        or frame.width * frame.height * 3 > frame_bytes
        or any(component.bits > MAX_COMPONENT_BITS for component in frame.format.components)
    ):
        msg = "frame_size"
        raise SourceError(msg)


def source_frames(reader: InputContainer, settings: SourceSettings) -> Iterator[tuple[av.VideoFrame, Fraction]]:
    """Select increasing source timestamps and skip duplicate browser timestamps without shifting later frames."""
    previous_time: Fraction | None = None
    origin: Fraction | None = None
    for frame in reader.decode(reader.streams.video[0]):
        if frame.pts is None or frame.time_base is None:
            msg = "source_time_missing"
            raise SourceError(msg)
        current = frame.pts * frame.time_base
        if origin is None:
            origin = current
        if previous_time is not None and (
            current < previous_time or (current == previous_time and not settings.browser_recording)
        ):
            msg = "timestamps"
            raise SourceError(msg)
        if current == previous_time:
            # MediaRecorder can give several frames one timestamp. Keep their original timeline.
            continue
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
    writer: VideoContainer,
    settings: SourceSettings,
) -> int:
    """Copy the chosen source interval while preserving usable frame timestamps."""
    frames = 0
    first_time: Fraction | None = None
    for frame, current in source_frames(reader, settings):
        if first_time is None:
            first_time = current
            output.width, output.height = frame.width, frame.height
        validate_frame(frame, output, settings.frame_bytes)
        frame.pts = round((current - first_time) * 1_000_000)
        frame.time_base = Fraction(1, 1_000_000)
        for packet in output.encode(frame):
            writer.mux(packet)
        frames += 1
        if frames > 120 * settings.duration_seconds + 1:
            msg = "source_frame_limit"
            raise SourceError(msg)
        if settings.destination.exists() and settings.destination.stat().st_size > settings.maximum_bytes:
            msg = "file_limit"
            raise SourceError(msg)
    if frames < (1 if settings.browser_recording else 33):
        raise SourceError("no_frames" if settings.browser_recording else "source_frames")
    for packet in output.encode():
        writer.mux(packet)
    return frames


def read_settings(arguments: list[str]) -> SourceSettings:
    """Parse the fixed worker command without accepting provider text or remote input paths."""
    if len(arguments) not in (7, 8) or (len(arguments) == BROWSER_WORKER_ARGUMENT_COUNT and arguments[7] != "browser"):
        msg = "source_video"
        raise SourceError(msg)
    return SourceSettings(
        source=Path(arguments[1]),
        destination=Path(arguments[2]),
        start_seconds=float(arguments[3]),
        duration_seconds=float(arguments[4]),
        maximum_bytes=int(arguments[5]),
        frame_bytes=int(arguments[6]),
        browser_recording=len(arguments) == BROWSER_WORKER_ARGUMENT_COUNT,
    )


def main(arguments: list[str]) -> int:
    """Accept only local paths and non-secret preparation limits."""
    sys.stdout.write(str(json.dumps({"ready": True})) + "\n")
    sys.stdout.flush()
    try:
        result = prepare(read_settings(arguments))
    except SourceError as error:
        sys.stdout.write(str(json.dumps({"error": str(error)})) + "\n")
        sys.stdout.flush()
        return 1
    except Exception:  # noqa: BLE001 -- reason: The worker protocol permits only fixed error codes, never native exception text.
        sys.stdout.write(str(json.dumps({"error": "source_video"})) + "\n")
        sys.stdout.flush()
        return 1
    sys.stdout.write(str(json.dumps(result)) + "\n")
    sys.stdout.flush()
    return 0
