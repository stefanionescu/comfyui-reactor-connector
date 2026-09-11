"""Read safe output facts after recording and remote cleanup finish."""

import sys
import asyncio
from pathlib import Path
from ...language import translate
from ...serialization import Json
from ..state import CaptureResult
from ...errors import ErrorCode, ConnectorError
from ..process import close_input, MediaProcess
from ....config.media.workers import METADATA_TIMEOUT_SECONDS
from ....config.media.capture import MAX_FRAME_DIMENSION, MIN_FRAME_DIMENSION, MAX_DURATION_MICROSECONDS


async def read_recording_metadata(result: CaptureResult, maximum_bytes: int) -> dict[str, Json]:
    """Bound header reading and return only documented numeric and Boolean fields."""
    worker = MediaProcess(
        [
            sys.executable,
            "-I",
            str(Path(__file__).parents[3]),
            "metadata",
            str(result.path),
            str(maximum_bytes),
        ]
    )
    try:
        async with asyncio.timeout(METADATA_TIMEOUT_SECONDS):
            payload = await worker.run(close_input, asyncio.Event(), asyncio.Event())
    except TimeoutError:
        raise ConnectorError(ErrorCode.CAPTURE, translate("main", "errors.savedVideoTimeout")) from None
    width, height, duration, size, audio = (
        payload.get("width"),
        payload.get("height"),
        payload.get("duration_us"),
        payload.get("file_bytes"),
        payload.get("has_audio"),
    )
    if (
        set(payload) != {"width", "height", "duration_us", "file_bytes", "has_audio"}
        or type(width) is not int
        or not MIN_FRAME_DIMENSION <= width <= MAX_FRAME_DIMENSION
        or type(height) is not int
        or not MIN_FRAME_DIMENSION <= height <= MAX_FRAME_DIMENSION
        or (duration is not None and (type(duration) is not int or not 0 < duration <= MAX_DURATION_MICROSECONDS))
        or type(size) is not int
        or not 0 < size <= maximum_bytes
        or type(audio) is not bool
    ):
        raise ConnectorError(ErrorCode.CAPTURE, translate("main", "errors.savedVideoDetails"))
    return {
        "frames": result.frames,
        "timestamp_mode": result.timestamp_mode,
        "width": width,
        "height": height,
        "duration_seconds": duration / 1_000_000 if duration is not None else None,
        "file_bytes": size,
        "has_audio": audio,
    }
