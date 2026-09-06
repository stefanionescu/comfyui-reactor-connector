"""Read safe output facts after recording and remote cleanup finish."""

import asyncio
import sys
from pathlib import Path

from ..errors import ConnectorError, ErrorCode
from ..json_data import Json
from .capture import CaptureResult
from .process import EncoderProcess


async def _no_input(writer: asyncio.StreamWriter) -> None:
    writer.write_eof()


async def recording_details(result: CaptureResult, maximum_bytes: int) -> dict[str, Json]:
    """Bound header reading and return only documented numeric and Boolean fields."""
    worker = EncoderProcess(
        [
            sys.executable,
            "-I",
            str(Path(__file__).with_name("metadata_worker.py")),
            str(result.path),
            str(maximum_bytes),
        ]
    )
    try:
        async with asyncio.timeout(10):
            data = await worker.run(_no_input, asyncio.Event(), asyncio.Event())
    except TimeoutError:
        raise ConnectorError(
            ErrorCode.CAPTURE, "Reading the saved video's details took too long."
        ) from None
    width, height, duration, size, audio = (
        data.get("width"),
        data.get("height"),
        data.get("duration_us"),
        data.get("file_bytes"),
        data.get("has_audio"),
    )
    if (
        set(data) != {"width", "height", "duration_us", "file_bytes", "has_audio"}
        or type(width) is not int
        or not 2 <= width <= 8192
        or type(height) is not int
        or not 2 <= height <= 8192
        or (
            duration is not None
            and (type(duration) is not int or not 0 < duration <= 3_601_000_000)
        )
        or type(size) is not int
        or not 0 < size <= maximum_bytes
        or type(audio) is not bool
    ):
        raise ConnectorError(ErrorCode.CAPTURE, "The saved video returned invalid details.")
    return {
        "frames": result.frames,
        "timestamp_mode": result.timestamp_mode,
        "width": width,
        "height": height,
        "duration_seconds": duration / 1_000_000 if duration is not None else None,
        "file_bytes": size,
        "has_audio": audio,
    }
