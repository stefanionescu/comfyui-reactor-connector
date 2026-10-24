"""Limit file size and finish pending writes before closing a cancelled output."""

from __future__ import annotations

from typing import TYPE_CHECKING, BinaryIO
import asyncio

from ..tasks import wait_shielded
from ..errors import ErrorCode, ConnectorError
from ..config.messages.media import OUTPUT_SIZE, OUTPUT_CLOSED

if TYPE_CHECKING:
    from types import TracebackType
    from typing import Self
    from pathlib import Path
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

    def _write(self, content: bytes) -> None:
        """Create the output on the first write without overwriting an existing file, then write while it is open."""
        if not self.created:
            self.stream = self.path.open('xb')
            self.created = True
        if self.stream is None:
            raise ConnectorError(ErrorCode.CAPTURE, OUTPUT_CLOSED)
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
        """Check the byte limit, then complete the write off the event loop before allowing cancellation."""
        if self.written + len(content) > self.maximum_bytes:
            raise ConnectorError(ErrorCode.CAPTURE, OUTPUT_SIZE)
        await owned_io(lambda: self._write(content))

    async def __aenter__(self) -> Self:
        """Create the output off the event loop and discard it if entry fails."""
        try:
            # An empty first write creates the file.
            await owned_io(lambda: self._write(b''))
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
    if await wait_shielded(task):
        task.exception()
        raise asyncio.CancelledError
    return task.result()


async def discard_outputs(*paths: Path, error: BaseException | None) -> None:
    """Attempt every owned output removal and preserve an existing execution failure."""

    def remove_files() -> None:
        """Finish all removals in one worker before returning the first filesystem error."""
        failure: OSError | None = None
        for path in paths:
            try:
                path.unlink(missing_ok=True)
            except OSError as exception:
                if failure is None:
                    failure = exception
        if failure is not None:
            raise failure

    try:
        await owned_io(remove_files)
    except OSError:
        if error is None:
            raise
        error.add_note('Some temporary recording files could not be removed.')
