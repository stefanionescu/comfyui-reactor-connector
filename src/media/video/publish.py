"""Publish a prepared local clip at its frame rate with one owned task."""

import asyncio
from pathlib import Path
from ..output import owned_io
from .frames import PreparedFrames
from collections.abc import Callable
from ...execution.transport import Track


class VideoPublication:
    """Repeat the final input frame until recording finishes or is cancelled."""

    def __init__(self) -> None:
        """Prepare ownership of the source publication task and its start signal."""
        self.task: asyncio.Task[None] | None = None
        self.started: asyncio.Event | None = None

    async def begin(self, path: Path, track: Track, fail: Callable[[object], None]) -> None:
        """Start the publisher and wait until the first frame is sent or setup fails."""
        ready = asyncio.Event()
        self.started = asyncio.Event()
        self.task = asyncio.create_task(self._run(path, track, fail, ready, self.started))
        await ready.wait()
        if self.task.done():
            await self.task

    def resume(self) -> None:
        """Allow timed playback after the model has accepted its initial configuration."""
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
        """Publish frames at their timestamps, repeat the final frame, and always close the reader."""
        reader = PreparedFrames(path)
        try:
            pixels, first_time = await owned_io(reader.open)
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
        except Exception as error:
            fail(error)
            raise
        finally:
            try:
                await owned_io(reader.close)
            finally:
                ready.set()

    async def close(self) -> None:
        """Cancel and await source publication before releasing its start signal."""
        task = self.task
        self.task = None
        self.started = None
        if task is not None:
            if not task.done():
                task.cancel()
            await asyncio.gather(task, return_exceptions=True)
