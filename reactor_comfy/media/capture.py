"""Queue copied video frames within memory limits for a separate encoder process."""

import asyncio
import queue
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import numpy as np
from numpy.typing import NDArray

from ..errors import ConnectorError, ErrorCode
from .encoding import FRAME_HEADER
from .process import EncoderProcess


@dataclass(frozen=True, slots=True)
class VideoFrame:
    """An owned RGB frame and its sender timestamp."""

    pixels: bytes
    width: int
    height: int
    timestamp_us: int


@dataclass(frozen=True, slots=True)
class CaptureResult:
    """File path, frame count, and timing method for the saved recording."""

    path: Path
    frames: int
    timestamp_mode: str
    audio_path: Path | None = None


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
        self.pending: queue.Queue[VideoFrame] = queue.Queue(maxsize=16)
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
                str(Path(__file__).with_name("encoding.py")),
                str(path),
                str(self.duration_us),
                str(queue_bytes),
                str(output_bytes),
                str(fallback_fps),
            ]
        )

    def receive(self, pixels: object, frame_id: int, timestamp_us: int, user_data: bytes) -> None:
        """Copy one SDK frame; reject it if the frame queue or memory limit is reached."""
        if self.stopped.is_set() or self.source_finished.is_set():
            return
        if not isinstance(pixels, np.ndarray):
            self.fail("The video track returned an unsupported frame.")
            return
        array = cast(NDArray[np.uint8], pixels)
        if array.dtype != np.uint8 or array.ndim != 3 or array.shape[2] != 3:
            self.fail("The video track must provide RGB frames.")
            return
        if type(timestamp_us) is not int or not 0 <= timestamp_us < 2**63:
            self.fail("The video track returned an invalid timestamp.")
            return
        with self.lock:
            if self.stopped.is_set() or self.source_finished.is_set():
                return
            if self.held_bytes + array.nbytes > self.queue_bytes:
                self.fail("Video arrived faster than it could be saved. Shorten the capture.")
                return
            owned = array.tobytes(order="C")
            try:
                height, width = array.shape[:2]
                self.pending.put_nowait(VideoFrame(owned, width, height, timestamp_us))
            except queue.Full:
                self.fail("The video capture queue is full. Shorten the capture.")
                return
            self.held_bytes += len(owned)
        self.loop.call_soon_threadsafe(self.frame_available.set)
        if not self._first_received:
            self._first_received = True
            self.loop.call_soon_threadsafe(self.first_frame.set)

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
            if self.failure:
                raise self.failure
            frames, mode = result.get("frames"), result.get("timestamp_mode")
            if type(frames) is not int or frames < 1 or mode not in ("sender", "fallback_fps"):
                raise ConnectorError(
                    ErrorCode.CAPTURE, "The video encoder returned invalid metadata."
                )
            self.frame_count, self.timestamp_mode = frames, str(mode)
            success = True
            return CaptureResult(self.path, frames, str(mode))
        except ConnectorError:
            if self.failure:
                raise self.failure from None
            raise
        except Exception:
            raise ConnectorError(
                ErrorCode.CAPTURE, "Video encoding failed. Check disk space and media support."
            ) from None
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
