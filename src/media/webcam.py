"""Hold the latest camera frame and publish it without storing camera footage."""

from __future__ import annotations

import io
import time
import asyncio
import threading
import numpy as np
from ..language import translate
from typing import TYPE_CHECKING
from PIL import Image, UnidentifiedImageError
from ..errors import ErrorCode, ConnectorError
from ...config.media.webcam import (
    MAX_CAMERA_WIDTH,
    MAX_CAMERA_HEIGHT,
    CAMERA_READY_SECONDS,
    MAX_CAMERA_JPEG_BYTES,
    CAMERA_TIMEOUT_SECONDS,
)

if TYPE_CHECKING:
    from numpy.typing import NDArray
    from collections.abc import Callable
    from ..execution.transport import Track


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
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.cameraFrameSize"))
        invalid = ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.cameraDimensions"))
        try:
            with Image.open(io.BytesIO(content)) as image:
                if (
                    image.format != "JPEG"
                    or not 1 <= image.width <= MAX_CAMERA_WIDTH
                    or not 1 <= image.height <= MAX_CAMERA_HEIGHT
                ):
                    raise invalid
                pixels = np.asarray(image.convert("RGB"), dtype=np.uint8).copy()
        except (OSError, ValueError, UnidentifiedImageError):
            raise invalid from None
        with self.lock:
            if self.closed or sequence <= self.sequence:
                raise ConnectorError(ErrorCode.UNAVAILABLE, translate("main", "errors.cameraFrameOrder"))
            self.sequence = sequence
            self.pixels = pixels
            self.received_at = time.monotonic()

    def is_ready(self) -> bool:
        """Require a recent camera frame before starting a session."""
        with self.lock:
            return (
                not self.closed
                and self.pixels is not None
                and time.monotonic() - self.received_at < CAMERA_READY_SECONDS
            )

    async def begin(self, track: Track, fail: Callable[[object], None]) -> None:
        """Start the camera publisher on the provider session event loop."""
        self.task = asyncio.create_task(self._publish(track, fail))

    def _current_frame(self) -> NDArray[np.uint8]:
        """Read the latest camera pixels and reject a closed, empty, or stale input."""
        with self.lock:
            pixels, age, closed = self.pixels, time.monotonic() - self.received_at, self.closed
        if closed or pixels is None or age > CAMERA_TIMEOUT_SECONDS:
            raise ConnectorError(ErrorCode.TRANSPORT, translate("main", "errors.cameraInputStopped"))
        return pixels

    async def _publish(self, track: Track, fail: Callable[[object], None]) -> None:
        """Send the latest frame at the camera rate and report missing or stale input."""
        try:
            while True:
                track.push_frame(self._current_frame())
                await asyncio.sleep(1 / 24)
        except asyncio.CancelledError:
            raise
        except Exception as error:  # noqa: BLE001 -- reason: Forward all publisher failures to the session owner so it terminates the session.
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
