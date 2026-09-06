"""Own local recording conversion after the remote session has closed."""

import asyncio
import sys
from pathlib import Path

from ..config import Settings
from ..errors import ConnectorError, ErrorCode
from .capture import CaptureResult
from .file_output import owned_io
from .process import EncoderProcess


async def _no_input(writer: asyncio.StreamWriter) -> None:
    writer.write_eof()


async def prepare_recording(
    source: Path,
    destination: Path,
    audio: Path,
    duration_seconds: float,
    settings: Settings,
    *,
    start_seconds: float = 0,
) -> CaptureResult:
    """Keep decoding terminable and remove both outputs after any failure."""
    worker = EncoderProcess(
        [
            sys.executable,
            "-I",
            str(Path(__file__).with_name("recording_worker.py")),
            str(source),
            str(destination),
            str(audio),
            str(duration_seconds),
            str(settings.max_capture_megabytes * 1_048_576),
            str(settings.max_queue_megabytes * 1_048_576),
            str(start_seconds),
        ]
    )
    success = False
    try:
        async with asyncio.timeout(60):
            result = await worker.run(_no_input, asyncio.Event(), asyncio.Event())
        frames, mode = result.get("frames"), result.get("timestamp_mode")
        samples, channels = result.get("audio_samples"), result.get("channels")
        if (
            type(frames) is not int
            or not 1 <= frames <= duration_seconds * 120 + 1
            or mode != "recording_pts"
            or result.get("sample_rate") != 48_000
            or type(samples) is not int
            or not 1 <= samples <= duration_seconds * 48_000 + 1
            or type(channels) is not int
            or channels not in (1, 2)
        ):
            raise ConnectorError(
                ErrorCode.CAPTURE, "The recording returned invalid media metadata."
            )
        success = True
        return CaptureResult(destination, frames, str(mode), audio_path=audio)
    finally:
        if not success:
            await owned_io(lambda: destination.unlink(missing_ok=True))
            await owned_io(lambda: audio.unlink(missing_ok=True))
