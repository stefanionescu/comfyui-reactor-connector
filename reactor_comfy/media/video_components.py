"""Encode native video tensors one frame at a time without duplicating the clip."""

import asyncio
import math
import sys
from functools import partial
from pathlib import Path

import numpy as np
from comfy_api.latest import Input, InputImpl

from ..config import Settings
from ..errors import ConnectorError, ErrorCode
from .encoding import FRAME_HEADER
from .file_output import owned_io
from .process import EncoderProcess


def _pixels(frame: Input.Image) -> bytes:
    array = frame.detach().cpu().numpy()
    if not np.isfinite(array).all():
        raise ConnectorError(ErrorCode.INVALID_INPUT, "Source pixels must be finite numbers.")
    return np.rint(np.clip(array, 0, 1) * 255).astype(np.uint8).tobytes(order="C")


async def prepare_components(
    video: InputImpl.VideoFromComponents, destination: Path, settings: Settings
) -> None:
    """Use native tensor components directly; omit audio from the uploaded edit source."""
    components = video.get_components()
    images, rate = components.images, components.frame_rate
    if (
        images.ndim != 4
        or images.shape[3] != 3
        or not 1 <= rate <= 120
        or video.get_bit_depth() != 8
        or video.get_color_space() != "sRGB"
    ):
        raise ConnectorError(
            ErrorCode.INVALID_INPUT, "Use an SDR RGB video at 1 to 120 frames per second."
        )
    total, height, width, _ = images.shape
    if (
        not 2 <= width <= 4096
        or not 2 <= height <= 4096
        or width % 2
        or height % 2
        or width * height * 3 > settings.max_queue_megabytes * 1_048_576
    ):
        raise ConnectorError(
            ErrorCode.INVALID_INPUT, "Use even video dimensions within the input limit."
        )
    count = min(total, math.ceil(settings.max_capture_seconds * rate))
    if count < 33:
        raise ConnectorError(ErrorCode.INVALID_INPUT, "Use a source video with at least 33 frames.")

    async def feed(writer: asyncio.StreamWriter) -> None:
        for index in range(count):
            pixels = await owned_io(partial(_pixels, images[index]))
            timestamp = 1_000_000 + round(index * 1_000_000 / rate)
            writer.write(FRAME_HEADER.pack(width, height, timestamp))
            writer.write(pixels)
            await writer.drain()
        writer.write_eof()

    worker = EncoderProcess(
        [
            sys.executable,
            "-I",
            str(Path(__file__).with_name("encoding.py")),
            str(destination),
            str(settings.max_capture_seconds * 1_000_000),
            str(settings.max_queue_megabytes * 1_048_576),
            str(settings.max_upload_megabytes * 1_048_576),
            str(round(rate)),
        ]
    )
    result = await worker.run(feed, asyncio.Event(), asyncio.Event())
    if result.get("frames") != count:
        raise ConnectorError(ErrorCode.CAPTURE, "The prepared source lost frames during encoding.")
