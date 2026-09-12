"""Prepare native ComfyUI video inputs before requesting a session."""

import io
import sys
import math
import asyncio
from pathlib import Path
from typing import BinaryIO
from ...language import translate
from ...paths import EXTENSION_ROOT
from ...state.settings import Settings
from tempfile import TemporaryDirectory
from ..output import owned_io, FileOutput
from .components import prepare_components
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from comfy_api.latest import Input, InputImpl
from ..units import convert_mebibytes_to_bytes
from ...errors import ErrorCode, ConnectorError
from ..process import close_input, MediaProcess
from ....config.media.workers import INPUT_TIMEOUT_SECONDS
from ....config.media.video import MIN_SOURCE_FRAMES, SOURCE_COPY_CHUNK_BYTES


def input_error() -> ConnectorError:
    """Describe the accepted local video input without exposing a source path."""
    return ConnectorError(
        ErrorCode.INVALID_INPUT,
        translate("main", "errors.localSourceRequired"),
    )


async def _copy_source(source: str | io.BytesIO, destination: Path, maximum: int) -> None:
    """Copy a local file or memory stream within the upload limit without blocking the host loop."""
    if isinstance(source, io.BytesIO):
        with source.getbuffer() as buffer:
            if buffer.nbytes > maximum:
                raise input_error()
            async with FileOutput(destination, maximum) as output:
                for offset in range(0, buffer.nbytes, SOURCE_COPY_CHUNK_BYTES):
                    await output.write(bytes(buffer[offset : offset + SOURCE_COPY_CHUNK_BYTES]))
        return
    await _copy_file(Path(source), destination, maximum)


async def _copy_file(path: Path, destination: Path, maximum: int) -> None:
    """Copy one local source off the host loop and retain stream ownership through cancellation."""
    valid = path.is_absolute() and await owned_io(lambda: path.is_file() and path.stat().st_size <= maximum)
    if not valid:
        raise input_error()
    stream: BinaryIO | None = None

    def open_source() -> None:
        """Retain the source stream so its owner can close it after cancellation."""
        nonlocal stream
        stream = path.open("rb")

    def read_chunk() -> bytes:
        """Read one chunk only after the source stream has opened."""
        if stream is None:
            raise input_error()
        return stream.read(SOURCE_COPY_CHUNK_BYTES)

    try:
        await owned_io(open_source)
        async with FileOutput(destination, maximum) as output:
            while chunk := await owned_io(read_chunk):
                await output.write(chunk)
    finally:
        if stream is not None:
            await owned_io(stream.close)


@asynccontextmanager
async def prepared_video(video: Input.Video, settings: Settings, temporary_root: Path) -> AsyncGenerator[Path]:
    """Own source and output copies until the model has finished using them."""
    if not isinstance(video, (InputImpl.VideoFromFile, InputImpl.VideoFromComponents)):
        raise input_error()
    maximum = convert_mebibytes_to_bytes(settings.max_upload_megabytes)
    with TemporaryDirectory(prefix="reactor-source-", dir=temporary_root) as directory:
        source = Path(directory) / "source.video"
        destination = Path(directory) / "input.mp4"
        try:
            async with asyncio.timeout(INPUT_TIMEOUT_SECONDS):
                if isinstance(video, InputImpl.VideoFromComponents):
                    await prepare_components(video, destination, settings)
                else:
                    await _prepare_file(video, source, destination, settings, maximum)
        except (OSError, ValueError):
            raise input_error() from None
        yield destination


async def _prepare_file(
    video: InputImpl.VideoFromFile,
    source: Path,
    destination: Path,
    settings: Settings,
    maximum: int,
) -> None:
    """Copy and trim a local source in an isolated worker before checking the required frame count."""
    await _copy_source(video.get_stream_source(), source, maximum)
    start, duration = await owned_io(video.get_active_trim_window)
    if not all(math.isfinite(value) and value >= 0 for value in (start, duration)):
        raise input_error()
    duration = min(duration or settings.max_capture_seconds, settings.max_capture_seconds)
    worker = MediaProcess(
        [
            sys.executable,
            "-I",
            str(EXTENSION_ROOT),
            "video",
            str(source),
            str(destination),
            str(start),
            str(duration),
            str(maximum),
            str(convert_mebibytes_to_bytes(settings.max_queue_megabytes)),
        ]
    )
    result = await worker.run(close_input, asyncio.Event(), asyncio.Event())
    frames = result.get("frames")
    if type(frames) is not int or frames < MIN_SOURCE_FRAMES:
        raise input_error()
