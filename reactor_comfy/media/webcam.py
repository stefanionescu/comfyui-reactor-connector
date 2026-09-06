"""Hold the latest camera frame and publish it without storing camera footage."""

import asyncio
import io
import threading
import time
from collections.abc import Callable

import numpy as np
from numpy.typing import NDArray
from PIL import Image, UnidentifiedImageError

from ..errors import ConnectorError, ErrorCode
from ..execution.transport import Track


class WebcamFrames:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.upload_lock = threading.Lock()
        self.pixels: NDArray[np.uint8] | None = None
        self.received_at = 0.0
        self.sequence = -1
        self.closed = False
        self.task: asyncio.Task[None] | None = None

    def receive(self, data: bytes, sequence: int) -> None:
        if not data or len(data) > 300_000:
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Send a camera JPEG smaller than 300 KB.")
        try:
            with Image.open(io.BytesIO(data)) as image:
                if (
                    image.format != "JPEG"
                    or not 1 <= image.width <= 640
                    or not 1 <= image.height <= 480
                ):
                    raise ValueError
                pixels = np.asarray(image.convert("RGB"), dtype=np.uint8).copy()
        except (OSError, ValueError, UnidentifiedImageError):
            raise ConnectorError(
                ErrorCode.INVALID_INPUT, "Send a JPEG no larger than 640 by 480 pixels."
            ) from None
        with self.lock:
            if self.closed or sequence <= self.sequence:
                raise ConnectorError(
                    ErrorCode.UNAVAILABLE, "The camera frame is out of order or the session ended."
                )
            self.sequence = sequence
            self.pixels = pixels
            self.received_at = time.monotonic()

    def is_ready(self) -> bool:
        with self.lock:
            return (
                not self.closed
                and self.pixels is not None
                and time.monotonic() - self.received_at < 2
            )

    async def begin(self, track: Track, fail: Callable[[object], None]) -> None:
        self.task = asyncio.create_task(self._publish(track, fail))

    async def _publish(self, track: Track, fail: Callable[[object], None]) -> None:
        try:
            while True:
                with self.lock:
                    pixels, age, closed = (
                        self.pixels,
                        time.monotonic() - self.received_at,
                        self.closed,
                    )
                if closed or pixels is None or age > 3:
                    raise ConnectorError(
                        ErrorCode.TRANSPORT, "Camera input stopped. The session is ending."
                    )
                track.push_frame(pixels)
                await asyncio.sleep(1 / 24)
        except asyncio.CancelledError:
            raise
        except Exception as error:
            fail(error)

    def clear(self) -> None:
        with self.lock:
            self.closed = True
            self.pixels = None

    async def close(self) -> None:
        self.clear()
        if self.task is not None:
            self.task.cancel()
            await asyncio.gather(self.task, return_exceptions=True)
            self.task = None
