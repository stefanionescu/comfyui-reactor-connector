"""Publish a prepared local clip at its frame rate with one owned task."""

import asyncio
from pathlib import Path
from dataclasses import field, dataclass
from collections.abc import Callable

from reactor_sdk import Track

from .frames import PreparedFrames
from ..output import owned_io


@dataclass(slots=True)
class VideoPublication:
    """Repeat the final input frame until the recording finishes or its task ends.

    Attributes:
        task: The source publication task, once it starts.
        started: Set when timed playback may begin, after the model accepts its initial configuration.

    """

    task: asyncio.Task[None] | None = None
    started: asyncio.Event = field(default_factory=asyncio.Event)

    async def begin(self, path: Path, track: Track, fail: Callable[[object], None]) -> None:
        """Start the publisher and wait until it sends the first frame or setup fails.

        Args:
            path: The prepared clip to publish.
            track: The track that receives the frames.
            fail: The callback that receives a publisher failure.

        """
        ready = asyncio.Event()
        self.started = asyncio.Event()
        self.task = asyncio.create_task(self._run(path, track, fail, ready, self.started))
        await ready.wait()
        if self.task.done():
            await self.task

    async def _run(
        self,
        path: Path,
        track: Track,
        fail: Callable[[object], None],
        ready: asyncio.Event,
        started: asyncio.Event,
    ) -> None:
        """Publish frames at their timestamps, repeat the final frame, and always close the reader.

        Args:
            path: The prepared clip to read.
            track: The track to push frames to.
            fail: The callback to call with any failure.
            ready: The event to set after the first frame or a failure.
            started: The event that allows timed playback.

        Raises:
            Exception: When reading or publishing fails.

        """
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
        self.started = asyncio.Event()
        if task is not None:
            if not task.done():
                task.cancel()
            await asyncio.gather(task, return_exceptions=True)
