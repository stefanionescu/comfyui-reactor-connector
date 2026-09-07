"""Own local recording conversion after the remote session has closed."""

import sys
import asyncio
from pathlib import Path
from ..output import owned_io
from functools import partial
from ...codes import ErrorCode
from ..capture import CaptureResult
from ...errors import ConnectorError
from ...settings.settings import Settings
from ....config.media.audio import SAMPLE_RATE
from ..process import close_input, EncoderProcess
from ....config.media.workers import RECORDING_TIMEOUT_SECONDS


async def prepare_recording(
    source: Path,
    destination: Path,
    duration_seconds: float,
    settings: Settings,
    *,
    start_seconds: float = 0,
) -> CaptureResult:
    """Keep decoding terminable and remove both outputs after any failure."""
    audio = destination.with_suffix(".wav")
    worker = EncoderProcess(
        [
            sys.executable,
            "-I",
            str(Path(__file__).parents[3]),
            "recording",
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
        async with asyncio.timeout(RECORDING_TIMEOUT_SECONDS):
            result = await worker.run(close_input, asyncio.Event(), asyncio.Event())
        frames, mode = result.get("frames"), result.get("timestamp_mode")
        samples, channels = result.get("audio_samples"), result.get("channels")
        if (
            type(frames) is not int
            or not 1 <= frames <= duration_seconds * 120 + 1
            or mode != "recording_pts"
            or result.get("sample_rate") != SAMPLE_RATE
            or type(samples) is not int
            or not 1 <= samples <= duration_seconds * 48_000 + 1
            or type(channels) is not int
            or channels not in (1, 2)
        ):
            raise ConnectorError(ErrorCode.CAPTURE, "The recording returned invalid media metadata.")
        success = True
        return CaptureResult(destination, frames, str(mode), audio_path=audio)
    finally:
        if not success:
            await owned_io(partial(destination.unlink, missing_ok=True))
            await owned_io(partial(audio.unlink, missing_ok=True))
