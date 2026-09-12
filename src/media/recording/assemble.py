"""Own local recording conversion after the remote session has closed."""

import sys
import asyncio
from pathlib import Path
from ...language import translate
from ...paths import EXTENSION_ROOT
from ..output import discard_outputs
from ...state.settings import Settings
from ...state.media import CaptureResult
from ..units import convert_mebibytes_to_bytes
from ...errors import ErrorCode, ConnectorError
from ..process import close_input, MediaProcess
from ....config.media.video import MAX_FRAME_RATE
from ....config.media.workers import RECORDING_TIMEOUT_SECONDS
from ....config.media.audio import SAMPLE_RATE, MAX_CHANNELS, MIN_CHANNELS


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
    worker = MediaProcess(
        [
            sys.executable,
            "-I",
            str(EXTENSION_ROOT),
            "recording",
            str(source),
            str(destination),
            str(audio),
            str(duration_seconds),
            str(convert_mebibytes_to_bytes(settings.max_capture_megabytes)),
            str(convert_mebibytes_to_bytes(settings.max_queue_megabytes)),
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
            or not 1 <= frames <= duration_seconds * MAX_FRAME_RATE + 1
            or mode != "recording_pts"
            or result.get("sample_rate") != SAMPLE_RATE
            or type(samples) is not int
            or not 1 <= samples <= duration_seconds * SAMPLE_RATE + 1
            or type(channels) is not int
            or not MIN_CHANNELS <= channels <= MAX_CHANNELS
        ):
            raise ConnectorError(ErrorCode.CAPTURE, translate("main", "errors.recordingMetadata"))
        success = True
        return CaptureResult(destination, frames, str(mode), audio_path=audio)
    finally:
        if not success:
            await discard_outputs(destination, audio, error=sys.exception())
