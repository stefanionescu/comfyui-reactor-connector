"""Publish a prepared local clip at its frame rate with one owned task."""

import asyncio
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import cast

import av
import numpy as np
from av.container.input import InputContainer
from numpy.typing import NDArray

from ..errors import ConnectorError, ErrorCode
from ..execution.transport import Track
from .file_output import owned_io


class PreparedFrames:
    """Decode only connector-prepared media, keeping one decoded frame in memory."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.container: InputContainer | None = None
        self.frames: Iterator[av.VideoFrame] | None = None
        self.step_seconds = 1 / 24

    def open(self) -> None:
        self.container = av.open(str(self.path), mode="r")
        rate = self.container.streams.video[0].average_rate
        if rate is None or not 1 <= rate <= 120:
            raise ConnectorError(
                ErrorCode.INVALID_INPUT, "The prepared video has no valid frame rate."
            )
        self.step_seconds = float(1 / rate)
        self.frames = iter(self.container.decode(video=0))

    def next(self) -> tuple[NDArray[np.uint8], float] | None:
        if self.frames is None:
            raise ConnectorError(ErrorCode.CAPTURE, "The prepared video reader is closed.")
        frame = next(self.frames, None)
        if frame is None:
            return None
        if frame.pts is None or frame.time_base is None:
            raise ConnectorError(ErrorCode.CAPTURE, "The prepared video has no frame timestamp.")
        return cast(NDArray[np.uint8], frame.to_ndarray(format="rgb24")), float(
            frame.pts * frame.time_base
        )

    def close(self) -> None:
        if self.container is not None:
            self.container.close()
        self.container = None
        self.frames = None


class VideoPublication:
    """Repeat the final input frame until recording finishes or is cancelled."""

    def __init__(self) -> None:
        self.task: asyncio.Task[None] | None = None
        self.started: asyncio.Event | None = None

    async def begin(self, path: Path, track: Track, fail: Callable[[object], None]) -> None:
        ready = asyncio.Event()
        self.started = asyncio.Event()
        self.task = asyncio.create_task(self._run(path, track, fail, ready, self.started))
        await ready.wait()
        if self.task.done():
            await self.task

    def resume(self) -> None:
        if self.started is not None:
            self.started.set()

    async def _run(
        self,
        path: Path,
        track: Track,
        fail: Callable[[object], None],
        ready: asyncio.Event,
        started: asyncio.Event,
    ) -> None:
        reader = PreparedFrames(path)
        try:
            await owned_io(reader.open)
            current = await owned_io(reader.next)
            if current is None:
                raise ConnectorError(ErrorCode.CAPTURE, "The prepared input has no frames.")
            pixels, first_time = current
            track.push_frame(pixels)
            ready.set()
            await started.wait()
            loop = asyncio.get_running_loop()
            origin = loop.time()
            relative = 0.0
            while True:
                current = await owned_io(reader.next)
                if current is None:
                    relative += reader.step_seconds
                else:
                    pixels, timestamp = current
                    relative = timestamp - first_time
                await asyncio.sleep(max(0.0, origin + relative - loop.time()))
                track.push_frame(pixels)
        except asyncio.CancelledError:
            raise
        except Exception as error:
            fail(error)
            raise
        finally:
            try:
                await owned_io(reader.close)
            finally:
                ready.set()

    async def close(self) -> None:
        task = self.task
        self.task = None
        self.started = None
        if task is not None:
            if not task.done():
                task.cancel()
            await asyncio.gather(task, return_exceptions=True)
