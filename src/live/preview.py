"""Keep a single reduced preview frame without slowing the capture recorder."""

import io
import math
import time
import base64
import threading
import numpy as np
from PIL import Image
from typing import cast, TYPE_CHECKING
from ...config.media.images import RGB_CHANNELS, MAX_FRAME_DIMENSION, RGB_ARRAY_DIMENSIONS

if TYPE_CHECKING:
    from numpy.typing import NDArray


class PreviewFrames:
    """Drop superseded preview frames; the separate recorder keeps its own policy."""

    def __init__(self) -> None:
        """Prepare a locked, single-frame preview buffer."""
        self.lock = threading.Lock()
        self.pending: NDArray[np.uint8] | None = None
        self.next_at = 0.0
        self.closed = False

    def receive(self, pixels: object, _frame_id: int, _timestamp_us: int, _user_data: bytes) -> None:
        """Keep a reduced copy of a valid RGB frame at the preview rate limit."""
        if not isinstance(pixels, np.ndarray):
            return
        array = cast("NDArray[np.uint8]", pixels)
        if array.dtype != np.uint8 or array.ndim != RGB_ARRAY_DIMENSIONS or array.shape[2] != RGB_CHANNELS:
            return
        height, width = array.shape[:2]
        if not 1 <= height <= MAX_FRAME_DIMENSION or not 1 <= width <= MAX_FRAME_DIMENSION:
            return
        with self.lock:
            now = time.monotonic()
            if self.closed or now < self.next_at:
                return
            self.next_at = now + 0.1
            stride = max(1, math.ceil(max(width / 640, height / 360)))
            self.pending = array[::stride, ::stride].copy()

    def encode(self) -> str:
        """Run image compression off the execution loop; retain no source metadata."""
        with self.lock:
            array, self.pending = self.pending, None
        if array is None:
            return ""
        with Image.fromarray(array) as image, io.BytesIO() as stream:
            image.save(stream, format="JPEG", quality=75)
            return base64.b64encode(stream.getvalue()).decode("ascii")

    def close(self) -> None:
        """Reject later frames and discard any pending preview."""
        with self.lock:
            self.closed = True
            self.pending = None
