"""Keep a single reduced preview frame without slowing the capture recorder."""

import base64
import io
import math
import threading
import time
from typing import cast

import numpy as np
from numpy.typing import NDArray
from PIL import Image


class PreviewFrames:
    """Drop superseded preview frames; the separate recorder keeps its own policy."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.pending: NDArray[np.uint8] | None = None
        self.next_at = 0.0
        self.closed = False

    def receive(self, pixels: object, frame_id: int, timestamp_us: int, user_data: bytes) -> None:
        if not isinstance(pixels, np.ndarray):
            return
        array = cast(NDArray[np.uint8], pixels)
        if array.dtype != np.uint8 or array.ndim != 3 or array.shape[2] != 3:
            return
        height, width = array.shape[:2]
        if not 1 <= height <= 8192 or not 1 <= width <= 8192:
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
        with self.lock:
            self.closed = True
            self.pending = None
