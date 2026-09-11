"""Encode native video tensors one frame at a time without duplicating the clip."""

import sys
import math
import struct
import asyncio
import numpy as np
from pathlib import Path
from ..output import owned_io
from functools import partial
from ...language import translate
from ..process import EncoderProcess
from ...settings.settings import Settings
from comfy_api.latest import Input, InputImpl
from ..units import convert_mebibytes_to_bytes
from ...errors import ErrorCode, ConnectorError
from ....config.media.capture import FRAME_HEADER_FORMAT
from ....config.media.images import RGB_CHANNELS, BATCH_IMAGE_DIMENSIONS
from ....config.media.video import (
    COMPONENT_BITS,
    MAX_FRAME_RATE,
    MIN_SOURCE_FRAMES,
    MAX_FRAME_DIMENSION,
    MIN_FRAME_DIMENSION,
)

FRAME_HEADER = struct.Struct(FRAME_HEADER_FORMAT)


def _pixels(frame: Input.Image) -> bytes:
    """Convert finite normalized image values to clipped RGB bytes."""
    array = frame.detach().cpu().numpy()
    if not np.isfinite(array).all():
        raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.sourcePixels"))
    return np.rint(np.clip(array, 0, 1) * 255).astype(np.uint8).tobytes(order="C")


async def prepare_components(video: InputImpl.VideoFromComponents, destination: Path, settings: Settings) -> None:
    """Use native tensor components directly; omit audio from the uploaded edit source."""
    components = video.get_components()
    images, rate = components.images, components.frame_rate
    if (
        images.ndim != BATCH_IMAGE_DIMENSIONS
        or images.shape[3] != RGB_CHANNELS
        or not 1 <= rate <= MAX_FRAME_RATE
        or video.get_bit_depth() != COMPONENT_BITS
        or video.get_color_space() != "sRGB"
    ):
        raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.sourceVideoFormat"))
    total, height, width, _ = images.shape
    if (
        not MIN_FRAME_DIMENSION <= width <= MAX_FRAME_DIMENSION
        or not MIN_FRAME_DIMENSION <= height <= MAX_FRAME_DIMENSION
        or width % 2
        or height % 2
        or width * height * 3 > convert_mebibytes_to_bytes(settings.max_queue_megabytes)
    ):
        raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.sourceDimensions"))
    count = min(total, math.ceil(settings.max_capture_seconds * rate))
    if count < MIN_SOURCE_FRAMES:
        raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.sourceFrameCount"))

    async def feed(writer: asyncio.StreamWriter) -> None:
        """Send selected tensor frames with timestamps and signal the end of input."""
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
            str(Path(__file__).parents[3]),
            "capture",
            str(destination),
            str(settings.max_capture_seconds * 1_000_000),
            str(convert_mebibytes_to_bytes(settings.max_queue_megabytes)),
            str(convert_mebibytes_to_bytes(settings.max_upload_megabytes)),
            str(round(rate)),
        ]
    )
    result = await worker.run(feed, asyncio.Event(), asyncio.Event())
    if result.get("frames") != count:
        raise ConnectorError(ErrorCode.CAPTURE, translate("main", "errors.sourceFramesLost"))
