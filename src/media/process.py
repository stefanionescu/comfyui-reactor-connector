"""Run the encoder in a separate process and enforce its shutdown deadline."""

import os
import asyncio
from contextlib import suppress
from ..tasks import wait_shielded
from ..state.documents import Json
from ..errors import ErrorCode, ConnectorError
from ..config.media.capture import ENCODER_ERRORS
from ..config.messages.session import CAPTURE_STOPPED
from ..serialization import parse_json, mapping_value
from collections.abc import Callable, Sequence, Coroutine
from ..config.media.workers import MAX_REPORT_BYTES, SHUTDOWN_TIMEOUT_SECONDS
from ..config.messages.media import ENCODER_PIPES, ENCODER_RESULT, ENCODER_NOT_READY, ENCODER_STOP_FAILED


class MediaProcess:
    """Run one isolated worker and reap it on success, failure, or cancellation."""

    def __init__(self, command: Sequence[str], shutdown_seconds: float = SHUTDOWN_TIMEOUT_SECONDS) -> None:
        """Record the fixed worker command and its shutdown deadline."""
        self.command = command
        self.shutdown_seconds = shutdown_seconds
        self.process: asyncio.subprocess.Process | None = None

    async def _reap(self) -> None:
        """Terminate the worker, escalate to kill if needed, and wait within the shutdown limits."""
        process = self.process
        if process is None or process.returncode is not None:
            return
        with suppress(ProcessLookupError):
            process.terminate()
        try:
            async with asyncio.timeout(self.shutdown_seconds):
                await process.wait()
        except TimeoutError:
            with suppress(ProcessLookupError):
                process.kill()
            try:
                async with asyncio.timeout(self.shutdown_seconds):
                    await process.wait()
            except TimeoutError:
                raise ConnectorError(
                    ErrorCode.CLEANUP,
                    ENCODER_STOP_FAILED,
                ) from None

    async def _dispose(self, tasks: Sequence[asyncio.Task[object]]) -> None:
        """Cancel pipe tasks, reap the worker, close stdin, and await every owned task."""
        for task in tasks:
            if not task.done():
                task.cancel()
        try:
            await self._reap()
        finally:
            if self.process is not None and self.process.stdin is not None:
                self.process.stdin.close()
            await asyncio.gather(*tasks, return_exceptions=True)

    async def run(
        self,
        ready: asyncio.Event,
        stopped: asyncio.Event,
        feed: Callable[[asyncio.StreamWriter], Coroutine[object, object, None]] | None = None,
    ) -> dict[str, Json]:
        """Observe input, result, and stop signals without blocking the host loop.

        Without a feed, the worker reads its input from files and stdin closes at once.
        """
        environment = {key: value for key, value in os.environ.items() if not key.startswith("REACTOR_")}
        self.process = await asyncio.create_subprocess_exec(
            *self.command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
            env=environment,
            limit=MAX_REPORT_BYTES,
        )
        tasks: list[asyncio.Task[object]] = []
        try:
            if self.process.stdin is None or self.process.stdout is None:
                raise ConnectorError(ErrorCode.CAPTURE, ENCODER_PIPES)
            reader = asyncio.create_task(_read_result(self.process.stdout, ready))
            interrupted = asyncio.create_task(stopped.wait())
            tasks.extend((reader, interrupted))
            if feed is None:
                self.process.stdin.write_eof()
            else:
                feeder = asyncio.create_task(feed(self.process.stdin))
                tasks.append(feeder)
                completed, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                if feeder in completed:
                    feeder.result()
            await asyncio.wait({reader, interrupted}, return_when=asyncio.FIRST_COMPLETED)
            if interrupted.done():
                raise ConnectorError(ErrorCode.CAPTURE, CAPTURE_STOPPED)
            result = await reader
            async with asyncio.timeout(self.shutdown_seconds):
                returncode = await self.process.wait()
            if returncode != 0:
                raise ConnectorError(ErrorCode.CAPTURE, ENCODER_ERRORS["encoder_failed"])
            return result
        finally:
            await self._finish(tasks)

    async def _finish(self, tasks: Sequence[asyncio.Task[object]]) -> None:
        """Await process disposal despite cancellation, then propagate cancellation or cleanup failure."""
        cleanup = asyncio.create_task(self._dispose(tasks))
        if await wait_shielded(cleanup):
            if not cleanup.cancelled():
                cleanup.exception()
            raise asyncio.CancelledError
        cleanup.result()


async def _report(reader: asyncio.StreamReader) -> dict[str, Json]:
    """Validate a size-limited worker report and translate fixed error codes into public errors."""
    line = await reader.readline()
    if not line or len(line) > MAX_REPORT_BYTES:
        raise ConnectorError(ErrorCode.CAPTURE, ENCODER_RESULT)
    try:
        value = mapping_value(parse_json(line.decode("utf-8"), max_bytes=MAX_REPORT_BYTES))
    except (ValueError, UnicodeError, ConnectorError):
        raise ConnectorError(ErrorCode.CAPTURE, ENCODER_RESULT) from None
    if "error" in value:
        code = value["error"]
        message = (
            ENCODER_ERRORS.get(code, ENCODER_ERRORS["encoder_failed"])
            if isinstance(code, str)
            else ENCODER_ERRORS["encoder_failed"]
        )
        raise ConnectorError(ErrorCode.CAPTURE, message)
    return value


async def _read_result(reader: asyncio.StreamReader, ready: asyncio.Event) -> dict[str, Json]:
    """Require the worker readiness message before accepting its final report."""
    initial = await _report(reader)
    if initial.keys() != {"ready"} or initial["ready"] is not True:
        raise ConnectorError(ErrorCode.CAPTURE, ENCODER_NOT_READY)
    ready.set()
    return await _report(reader)
