"""Queue copied video frames within memory limits for a separate encoder process."""

from __future__ import annotations

import sys
import queue
import struct
import asyncio
import threading
import numpy as np
from pathlib import Path
from ..language import translate
from .process import EncoderProcess
from typing import cast, TYPE_CHECKING
from .state import VideoFrame, CaptureResult
from ..errors import ErrorCode, ConnectorError
from ...config.media.images import RGB_CHANNELS, RGB_ARRAY_DIMENSIONS
from ...config.media.capture import MAX_QUEUED_FRAMES, FRAME_HEADER_FORMAT

FRAME_HEADER = struct.Struct(FRAME_HEADER_FORMAT)

if TYPE_CHECKING:
    from ..serialization import Json
    from numpy.typing import NDArray


class VideoCapture:
    """Bridge the native delivery thread to an incremental file encoder."""

    def __init__(
        self,
        path: Path,
        duration_seconds: float,
        queue_bytes: int,
        output_bytes: int,
        fallback_fps: int = 24,
    ) -> None:
        """Create frame buffers, cross-thread signals, and an isolated encoder with capture limits."""
        self.path = path
        self.duration_us = round(duration_seconds * 1_000_000)
        self.queue_bytes = queue_bytes
        self.output_bytes = output_bytes
        self.fallback_fps = fallback_fps
        self.first_frame = asyncio.Event()
        self.ready = asyncio.Event()
        self.complete = asyncio.Event()
        self.frame_available = asyncio.Event()
        self.stop_requested = asyncio.Event()
        self.loop = asyncio.get_running_loop()
        self.pending: queue.Queue[VideoFrame] = queue.Queue(maxsize=MAX_QUEUED_FRAMES)
        self.stopped = threading.Event()
        self.source_finished = threading.Event()
        self.lock = threading.Lock()
        self.held_bytes = 0
        self.failure: ConnectorError | None = None
        self.frame_count = 0
        self.timestamp_mode = "sender"
        self._first_received = False
        self.encoder = EncoderProcess(
            [
                sys.executable,
                "-I",
                str(Path(__file__).parents[2]),
                "capture",
                str(path),
                str(self.duration_us),
                str(queue_bytes),
                str(output_bytes),
                str(fallback_fps),
            ]
        )

    def receive(self, pixels: object, _frame_id: int, timestamp_us: int, _user_data: bytes) -> None:
        """Copy one SDK frame; reject it if the frame queue or memory limit is reached."""
        if self.stopped.is_set() or self.source_finished.is_set():
            return
        try:
            array = frame_pixels(pixels, timestamp_us)
            if not self._queue_frame(array, timestamp_us):
                return
        except ConnectorError as error:
            self.fail(str(error))
            return
        self.loop.call_soon_threadsafe(self.frame_available.set)
        if not self._first_received:
            self._first_received = True
            self.loop.call_soon_threadsafe(self.first_frame.set)

    def _queue_frame(self, array: NDArray[np.uint8], timestamp_us: int) -> bool:
        """Reserve memory and copy a frame while holding the capture queue lock."""
        with self.lock:
            if self.stopped.is_set() or self.source_finished.is_set():
                return False
            if self.held_bytes + array.nbytes > self.queue_bytes:
                raise ConnectorError(ErrorCode.CAPTURE, translate("main", "errors.videoArrivalRate"))
            owned = array.tobytes(order="C")
            try:
                height, width = array.shape[:2]
                self.pending.put_nowait(VideoFrame(owned, width, height, timestamp_us))
            except queue.Full:
                raise ConnectorError(ErrorCode.CAPTURE, translate("main", "errors.captureQueueFull")) from None
            self.held_bytes += len(owned)
        return True

    def _result(self, result: dict[str, Json]) -> CaptureResult:
        """Require valid encoder metadata and preserve any earlier frame-delivery failure."""
        if self.failure:
            raise self.failure
        frames, mode = result.get("frames"), result.get("timestamp_mode")
        if type(frames) is not int or frames < 1 or mode not in ("sender", "fallback_fps"):
            raise ConnectorError(ErrorCode.CAPTURE, translate("main", "errors.encoderMetadata"))
        self.frame_count, self.timestamp_mode = frames, str(mode)
        return CaptureResult(self.path, frames, str(mode))

    def fail(self, message: str) -> None:
        """Stop capture with a safe error that the event-loop owner can observe."""
        self.failure = ConnectorError(ErrorCode.CAPTURE, message)
        self.stop()
        self.loop.call_soon_threadsafe(self.first_frame.set)
        self.loop.call_soon_threadsafe(self.complete.set)

    def stop(self) -> None:
        """Stop waiting for more frames during cancellation or teardown."""
        self.stopped.set()
        self.loop.call_soon_threadsafe(self.stop_requested.set)
        self.loop.call_soon_threadsafe(self.frame_available.set)

    def finish(self) -> None:
        """Finish the file after draining accepted frames when a finite source ends."""
        with self.lock:
            self.source_finished.set()
        self.loop.call_soon_threadsafe(self.frame_available.set)

    async def encode(self) -> CaptureResult:
        """Return only after the encoder has finalized its file and exited."""
        success = False
        try:
            result = await self.encoder.run(self._feed, self.ready, self.stop_requested)
            captured = self._result(result)
        except ConnectorError:
            failure = self.failure
            if failure is not None:
                raise failure from None
            raise
        except Exception:  # noqa: BLE001 -- reason: Translate native encoder failures without exposing paths or native error text.
            raise ConnectorError(ErrorCode.CAPTURE, translate("main", "errors.videoEncodingFailed")) from None
        else:
            success = True
            return captured
        finally:
            self.stopped.set()
            with self.lock:
                while not self.pending.empty():
                    self.pending.get_nowait()
                self.held_bytes = 0
            try:
                if not success:
                    await asyncio.to_thread(self.path.unlink, missing_ok=True)
            finally:
                self.ready.set()
                self.first_frame.set()
                self.complete.set()

    async def _feed(self, writer: asyncio.StreamWriter) -> None:
        """Stream queued frames to the encoder and release their reserved memory after each write."""
        while not self.stopped.is_set():
            self.frame_available.clear()
            try:
                frame = self.pending.get_nowait()
            except queue.Empty:
                if self.source_finished.is_set():
                    writer.write_eof()
                    return
                await self.frame_available.wait()
                continue
            try:
                try:
                    writer.write(FRAME_HEADER.pack(frame.width, frame.height, frame.timestamp_us))
                    writer.write(frame.pixels)
                    await writer.drain()
                except (BrokenPipeError, ConnectionResetError):
                    # The child may have reached the requested duration. Its report decides success.
                    return
            finally:
                with self.lock:
                    self.held_bytes -= len(frame.pixels)


def frame_pixels(pixels: object, timestamp_us: int) -> NDArray[np.uint8]:
    """Require an RGB byte array and a nonnegative sender timestamp before copying a frame."""
    if not isinstance(pixels, np.ndarray):
        raise ConnectorError(ErrorCode.CAPTURE, translate("main", "errors.videoFrameType"))
    array = cast("NDArray[np.uint8]", pixels)
    if array.dtype != np.uint8 or array.ndim != RGB_ARRAY_DIMENSIONS or array.shape[2] != RGB_CHANNELS:
        raise ConnectorError(ErrorCode.CAPTURE, translate("main", "errors.videoFrameColor"))
    if type(timestamp_us) is not int or not 0 <= timestamp_us < 2**63:
        raise ConnectorError(ErrorCode.CAPTURE, translate("main", "errors.videoTimestamp"))
    return array
