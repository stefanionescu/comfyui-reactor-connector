"""Read header facts from a completed connector MP4 in a terminable process."""

import av
import sys
import json
from pathlib import Path
from ..protocol import report_outcome
from ...config.media.capture import MAX_FRAME_DIMENSION, MIN_FRAME_DIMENSION, MAX_DURATION_MICROSECONDS


WORKER_ARGUMENT_COUNT = 3


def describe(path: Path, maximum_bytes: int) -> dict[str, int | bool | None]:
    """Use the saved video stream's clock; never infer duration from frame count."""
    size = path.stat().st_size
    if not 0 < size <= maximum_bytes:
        raise ValueError
    with (
        path.open("rb") as file,
        av.open(file, mode="r", format="mp4", options={"protocol_whitelist": "pipe"}) as reader,
    ):
        if len(reader.streams.video) != 1 or len(reader.streams.audio) > 1:
            raise ValueError
        stream = reader.streams.video[0]
        width, height = stream.codec_context.width, stream.codec_context.height
        if (
            not MIN_FRAME_DIMENSION <= width <= MAX_FRAME_DIMENSION
            or not MIN_FRAME_DIMENSION <= height <= MAX_FRAME_DIMENSION
        ):
            raise ValueError
        duration_us = None
        if stream.duration is not None and stream.time_base is not None:
            duration_us = round(stream.duration * stream.time_base * 1_000_000)
            if not 0 < duration_us <= MAX_DURATION_MICROSECONDS:
                raise ValueError
        return {
            "width": width,
            "height": height,
            "duration_us": duration_us,
            "file_bytes": size,
            "has_audio": bool(reader.streams.audio),
        }


def main(arguments: list[str]) -> int:
    """Read worker arguments and report only fixed error codes or validated video facts."""
    sys.stdout.write(json.dumps({"ready": True}) + "\n")
    sys.stdout.flush()
    return report_outcome(lambda: _describe_arguments(arguments), fallback_code="recording_details")


def _describe_arguments(arguments: list[str]) -> dict[str, int | bool | None]:
    """Describe the recording named by a complete worker command."""
    if len(arguments) != WORKER_ARGUMENT_COUNT:
        raise ValueError(arguments)
    return describe(Path(arguments[1]), int(arguments[2]))
