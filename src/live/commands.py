"""Preserve each camera axis's order while independent axes await replies separately."""

import time
import asyncio
from ..execution.events import SessionEvents
from ..errors import ErrorCode, ConnectorError
from ..state.live import BrowserInput, CameraChange
from ..config.messages.live import CAMERA_INPUT_STALE, CAMERA_COMMAND_LIMIT, CAMERA_COMMAND_TIMEOUT
from ..config.live import MAX_QUEUED_MOVEMENTS, COMMAND_TIMEOUT_SECONDS, MAX_QUEUED_MOVEMENT_SECONDS


class CameraCommands:
    """Send commands for each supported camera axis with a separate queue and worker."""

    def __init__(self, axes: tuple[str, ...], events: SessionEvents) -> None:
        """Start a separate ordered command worker for each camera axis."""
        self.events = events
        self.queues = {axis: asyncio.Queue[CameraChange](maxsize=MAX_QUEUED_MOVEMENTS) for axis in axes}
        self.desired = dict.fromkeys(axes, "idle")
        self.workers = [asyncio.create_task(self._axis(axis)) for axis in axes]

    def submit(self, state: BrowserInput) -> None:
        """Queue changed axes, clearing earlier motion when the user releases controls."""
        for axis, value in state.axes:
            queue = self.queues[axis]
            if state.release:
                while not queue.empty():
                    queue.get_nowait()
            if state.release or self.desired[axis] != value:
                try:
                    queue.put_nowait(CameraChange(value, time.monotonic()))
                except asyncio.QueueFull:
                    raise ConnectorError(ErrorCode.UNAVAILABLE, CAMERA_COMMAND_LIMIT) from None
                self.desired[axis] = value

    async def _axis(self, axis: str) -> None:
        """Send one axis in order and report stale input or unacknowledged commands."""
        current = "idle"
        try:
            while True:
                change = await self.queues[axis].get()
                if change.value == current:
                    continue
                await self._apply(axis, change)
                current = change.value
        except asyncio.CancelledError:
            raise
        except ConnectorError as error:
            self.events.on_error(error)
        except TimeoutError:
            self.events.on_error(ConnectorError(ErrorCode.TIMEOUT, CAMERA_COMMAND_TIMEOUT))

    async def _apply(self, axis: str, change: CameraChange) -> None:
        """Send fresh camera input and wait for Reactor to acknowledge it."""
        if change.value != "idle" and time.monotonic() - change.queued_at > MAX_QUEUED_MOVEMENT_SECONDS:
            raise ConnectorError(ErrorCode.TIMEOUT, CAMERA_INPUT_STALE)
        async with asyncio.timeout(COMMAND_TIMEOUT_SECONDS):
            await self.events.command_reply(f"set_{axis}", {axis: change.value})

    async def stop(self) -> None:
        """Cancel and await all axis workers, then discard queued movement."""
        for worker in self.workers:
            worker.cancel()
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
        for queue in self.queues.values():
            while not queue.empty():
                queue.get_nowait()
