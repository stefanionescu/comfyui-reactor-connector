"""Prepare native ComfyUI video inputs before requesting a session."""

import io
import sys
import math
from typing import BinaryIO
import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from comfy_api.latest import Input, InputImpl

from ...paths import EXTENSION_ROOT
from ..output import FileOutput, owned_io
from ...errors import ErrorCode, ConnectorError
from ..process import MediaProcess
from .components import prepare_components
from ...config.nodes import MAX_DURATION_SECONDS
from ...state.settings import Settings
from ...config.settings import BYTES_PER_MEBIBYTE
from ...config.media.video import MIN_SOURCE_FRAMES, SOURCE_COPY_CHUNK_BYTES
from ...config.media.capture import MAX_QUEUE_BYTES
from ...config.media.workers import INPUT_TIMEOUT_SECONDS
from ...config.messages.media import LOCAL_SOURCE_REQUIRED


async def _copy_source(source: str | io.BytesIO, destination: Path, maximum: int) -> None:
    """Copy a local file or memory stream within the upload limit without blocking the host loop.

    Args:
        source: The path or the memory stream to copy.
        destination: The file to create.
        maximum: The largest source to accept, in bytes.

    Raises:
        ConnectorError: When the memory stream exceeds the limit.

    """
    if isinstance(source, io.BytesIO):
        with source.getbuffer() as buffer:
            if buffer.nbytes > maximum:
                raise ConnectorError(ErrorCode.INVALID_INPUT, LOCAL_SOURCE_REQUIRED)
            async with FileOutput(destination, maximum) as output:
                for offset in range(0, buffer.nbytes, SOURCE_COPY_CHUNK_BYTES):
                    await output.write(bytes(buffer[offset : offset + SOURCE_COPY_CHUNK_BYTES]))
        return
    await _copy_file(Path(source), destination, maximum)


async def _copy_file(path: Path, destination: Path, maximum: int) -> None:
    """Copy one local source off the host loop and retain stream ownership through cancellation.

    Args:
        path: The local source file.
        destination: The copy to create.
        maximum: The largest file to accept, in bytes.

    Raises:
        ConnectorError: When the path is not an absolute file within the limit.

    """
    valid = path.is_absolute() and await owned_io(lambda: path.is_file() and path.stat().st_size <= maximum)
    if not valid:
        raise ConnectorError(ErrorCode.INVALID_INPUT, LOCAL_SOURCE_REQUIRED)
    # The opening thread adds the stream here, so the owner closes it even when cancellation interrupts the wait.
    streams: list[BinaryIO] = []

    def read_chunk() -> bytes:
        """Read one chunk only after the source stream has opened.

        Returns:
            The next bytes, or empty bytes at the end of the file.

        Raises:
            ConnectorError: When no stream is open.

        """
        if not streams:
            raise ConnectorError(ErrorCode.INVALID_INPUT, LOCAL_SOURCE_REQUIRED)
        return streams[0].read(SOURCE_COPY_CHUNK_BYTES)

    try:
        await owned_io(lambda: streams.append(path.open('rb')))
        async with FileOutput(destination, maximum) as output:
            while chunk := await owned_io(read_chunk):
                await output.write(chunk)
    finally:
        for stream in streams:
            await owned_io(stream.close)


@asynccontextmanager
async def prepared_video(video: Input.Video, settings: Settings, temporary_root: Path) -> AsyncGenerator[Path]:
    """Own source and output copies until the model has finished using them.

    Args:
        video: The ComfyUI video input.
        settings: The settings that hold the upload size limit.
        temporary_root: The folder that holds the temporary copies.

    Yields:
        The prepared MP4 file.

    Raises:
        ConnectorError: When the input is not a supported local video.

    """
    if not isinstance(video, (InputImpl.VideoFromFile, InputImpl.VideoFromComponents)):
        raise ConnectorError(ErrorCode.INVALID_INPUT, LOCAL_SOURCE_REQUIRED)
    maximum = settings.max_upload_megabytes * BYTES_PER_MEBIBYTE
    with TemporaryDirectory(prefix='reactor-source-', dir=temporary_root) as directory:
        source = Path(directory) / 'source.video'
        destination = Path(directory) / 'input.mp4'
        try:
            async with asyncio.timeout(INPUT_TIMEOUT_SECONDS):
                if isinstance(video, InputImpl.VideoFromComponents):
                    await prepare_components(video, destination, settings)
                else:
                    await _prepare_file(video, source, destination, maximum)
        except (OSError, ValueError):
            raise ConnectorError(ErrorCode.INVALID_INPUT, LOCAL_SOURCE_REQUIRED) from None
        yield destination


async def _prepare_file(
    video: InputImpl.VideoFromFile,
    source: Path,
    destination: Path,
    maximum: int,
) -> None:
    """Copy and trim a local source in an isolated worker before checking the required frame count.

    Args:
        video: The video that a file or a memory stream backs.
        source: The path for the copy of the original.
        destination: The MP4 file that the worker writes.
        maximum: The largest input or output file, in bytes.

    Raises:
        ConnectorError: When the trim window is invalid or too few frames remain.

    """
    await _copy_source(video.get_stream_source(), source, maximum)
    start, duration = await owned_io(video.get_active_trim_window)
    if not all(math.isfinite(value) and value >= 0 for value in (start, duration)):
        raise ConnectorError(ErrorCode.INVALID_INPUT, LOCAL_SOURCE_REQUIRED)
    duration = min(duration or MAX_DURATION_SECONDS, MAX_DURATION_SECONDS)
    worker = MediaProcess(
        [
            sys.executable,
            '-I',
            str(EXTENSION_ROOT),
            'video',
            str(source),
            str(destination),
            str(start),
            str(duration),
            str(maximum),
            str(MAX_QUEUE_BYTES),
        ]
    )
    result = await worker.run(asyncio.Event(), asyncio.Event())
    frames = result.get('frames')
    if type(frames) is not int or frames < MIN_SOURCE_FRAMES:
        raise ConnectorError(ErrorCode.INVALID_INPUT, LOCAL_SOURCE_REQUIRED)
