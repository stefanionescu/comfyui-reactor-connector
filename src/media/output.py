"""Limit file size and finish pending writes before closing a cancelled output."""

from __future__ import annotations

import asyncio
from ..language import translate
from typing import BinaryIO, TYPE_CHECKING
from ..errors import ErrorCode, ConnectorError

if TYPE_CHECKING:
    from pathlib import Path
    from types import TracebackType
    from collections.abc import Callable


class FileOutput:
    """Create a new file and remove it if writing fails; preserve existing files."""

    def __init__(self, path: Path, maximum_bytes: int) -> None:
        """Prepare exclusive file creation and a maximum output size."""
        self.path = path
        self.maximum_bytes = maximum_bytes
        self.written = 0
        self.created = False
        self.stream: BinaryIO | None = None

    def _open(self) -> None:
        """Create a new output without overwriting an existing file."""
        self.stream = self.path.open("xb")
        self.created = True

    def _write(self, content: bytes) -> None:
        """Write only while the output is open and the byte limit allows it."""
        if self.stream is None:
            raise ConnectorError(ErrorCode.CAPTURE, translate("main", "errors.outputClosed"))
        if self.written + len(content) > self.maximum_bytes:
            raise ConnectorError(ErrorCode.CAPTURE, translate("main", "errors.outputSize"))
        self.stream.write(content)
        self.written += len(content)

    def _close(self, *, discard: bool) -> None:
        """Close the stream and remove only this output when writing or closing fails."""
        try:
            if self.stream is not None:
                self.stream.close()
        except BaseException:
            discard = True
            raise
        finally:
            self.stream = None
            if discard and self.created:
                self.path.unlink(missing_ok=True)

    async def write(self, content: bytes) -> None:
        """Complete the submitted write off the event loop before allowing cancellation."""
        await owned_io(lambda: self._write(content))

    async def __aenter__(self) -> FileOutput:
        """Create the output off the event loop and discard it if entry fails."""
        try:
            await owned_io(self._open)
        except BaseException:
            await owned_io(lambda: self._close(discard=True))
            raise
        return self

    async def __aexit__(
        self,
        _exception_type: type[BaseException] | None,
        exception: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        """Finish pending file ownership and remove the output after a failed operation."""
        try:
            await owned_io(lambda: self._close(discard=exception is not None))
        except BaseException:
            await owned_io(lambda: self._close(discard=True))
            raise


async def owned_io[T](operation: Callable[[], T]) -> T:
    """Do not close or remove a file while an already submitted write still owns it."""
    task = asyncio.create_task(asyncio.to_thread(operation))
    cancelled = False
    while not task.done():
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError:
            cancelled = True
        except Exception:  # noqa: BLE001 -- reason: Read the task result below after resolving ownership and pending cancellation.
            break
    if cancelled:
        task.exception()
        raise asyncio.CancelledError
    return task.result()
