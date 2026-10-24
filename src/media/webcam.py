"""Hold the latest camera frame and publish it without storing camera footage."""

from __future__ import annotations

import io
import time
from typing import TYPE_CHECKING
import asyncio
import threading

from PIL import Image, UnidentifiedImageError
import numpy as np

from ..errors import ErrorCode, ConnectorError
from ..config.media.webcam import (
    MAX_CAMERA_WIDTH,
    CAMERA_FRAME_RATE,
    MAX_CAMERA_HEIGHT,
    MAX_CAMERA_JPEG_BYTES,
    CAMERA_TIMEOUT_SECONDS,
)
from ..config.messages.live import CAMERA_DIMENSIONS, CAMERA_FRAME_SIZE, CAMERA_FRAME_ORDER, CAMERA_INPUT_STOPPED

if TYPE_CHECKING:
    from collections.abc import Callable

    from reactor_sdk import Track
    from numpy.typing import NDArray


class WebcamFrames:
    """Receive and queue a limited number of webcam frames for one model session."""

    def __init__(self) -> None:
        """Create a locked latest-frame buffer and a separate upload lock."""
        self.lock = threading.Lock()
        self.upload_lock = threading.Lock()
        self.pixels: NDArray[np.uint8] | None = None
        self.received_at = 0.0
        self.sequence = -1
        self.closed = False
        self.task: asyncio.Task[None] | None = None

    def receive(self, content: bytes, sequence: int) -> None:
        """Decode a size-limited JPEG and accept only a newer frame for an open session."""
        if not content or len(content) > MAX_CAMERA_JPEG_BYTES:
            raise ConnectorError(ErrorCode.INVALID_INPUT, CAMERA_FRAME_SIZE)
        invalid = ConnectorError(ErrorCode.INVALID_INPUT, CAMERA_DIMENSIONS)
        try:
            with Image.open(io.BytesIO(content)) as image:
                if (
                    image.format != 'JPEG'
                    or not 1 <= image.width <= MAX_CAMERA_WIDTH
                    or not 1 <= image.height <= MAX_CAMERA_HEIGHT
                ):
                    raise invalid
                pixels = np.asarray(image.convert('RGB'), dtype=np.uint8).copy()
        except (OSError, ValueError, UnidentifiedImageError):
            raise invalid from None
        with self.lock:
            if self.closed or sequence <= self.sequence:
                raise ConnectorError(ErrorCode.UNAVAILABLE, CAMERA_FRAME_ORDER)
            self.sequence = sequence
            self.pixels = pixels
            self.received_at = time.monotonic()

    def _current_frame(self) -> NDArray[np.uint8]:
        """Read the latest camera pixels and reject a closed, empty, or stale input."""
        with self.lock:
            pixels, age, closed = self.pixels, time.monotonic() - self.received_at, self.closed
        if closed or pixels is None or age > CAMERA_TIMEOUT_SECONDS:
            raise ConnectorError(ErrorCode.TRANSPORT, CAMERA_INPUT_STOPPED)
        return pixels

    async def publish(self, track: Track, fail: Callable[[object], None]) -> None:
        """Send the latest frame at the camera rate and report missing or stale input."""
        try:
            while True:
                track.push_frame(self._current_frame())
                await asyncio.sleep(1 / CAMERA_FRAME_RATE)
        except asyncio.CancelledError:
            raise
        except Exception as error:  # noqa: BLE001 # reason: Forward all publisher failures to the session owner so it terminates the session.
            fail(error)

    def clear(self) -> None:
        """Reject further frames and release retained camera pixels."""
        with self.lock:
            self.closed = True
            self.pixels = None

    async def close(self) -> None:
        """Clear camera pixels, cancel the publisher, and await its completion."""
        self.clear()
        if self.task is not None:
            self.task.cancel()
            await asyncio.gather(self.task, return_exceptions=True)
            self.task = None
