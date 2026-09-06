"""Limit file size and finish pending writes before closing a cancelled output."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from pathlib import Path
from types import TracebackType
from typing import BinaryIO

from ..errors import ConnectorError, ErrorCode


async def owned_io[T](operation: Callable[[], T]) -> T:
    """Do not close or remove a file while an already submitted write still owns it."""
    task = asyncio.create_task(asyncio.to_thread(operation))
    cancelled = False
    while not task.done():
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError:
            cancelled = True
        except Exception:
            break
    if cancelled:
        task.exception()
        raise asyncio.CancelledError
    return task.result()


class FileOutput:
    """Create a new file and remove it if writing fails; preserve existing files."""

    def __init__(self, path: Path, maximum_bytes: int) -> None:
        self.path = path
        self.maximum_bytes = maximum_bytes
        self.written = 0
        self.created = False
        self.stream: BinaryIO | None = None

    def _open(self) -> None:
        self.stream = self.path.open("xb")
        self.created = True

    def _write(self, data: bytes) -> None:
        if self.stream is None:
            raise ConnectorError(ErrorCode.CAPTURE, "The recording output is closed.")
        if self.written + len(data) > self.maximum_bytes:
            raise ConnectorError(ErrorCode.CAPTURE, "The recording exceeds the output size limit.")
        self.stream.write(data)
        self.written += len(data)

    def _close(self, discard: bool) -> None:
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

    async def write(self, data: bytes) -> None:
        await owned_io(lambda: self._write(data))

    async def __aenter__(self) -> FileOutput:
        try:
            await owned_io(self._open)
        except BaseException:
            await owned_io(lambda: self._close(discard=True))
            raise
        return self

    async def __aexit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        try:
            await owned_io(lambda: self._close(discard=exception is not None))
        except BaseException:
            await owned_io(lambda: self._close(discard=True))
            raise
