"""Run the encoder in a separate process and enforce its shutdown deadline."""

import asyncio
import os
from collections.abc import Callable, Coroutine, Sequence
from contextlib import suppress

from ..errors import ConnectorError, ErrorCode
from ..json_data import Json, object_value, parse_json
from .encoding import ENCODER_ERRORS


async def _report(reader: asyncio.StreamReader) -> dict[str, Json]:
    try:
        line = await reader.readline()
        if not line or len(line) > 4096:
            raise ValueError("Invalid report size.")
        value = object_value(parse_json(line.decode("utf-8"), max_bytes=4096))
    except (ValueError, UnicodeError, ConnectorError):
        raise ConnectorError(
            ErrorCode.CAPTURE, "The video encoder returned no valid result."
        ) from None
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
    initial = await _report(reader)
    if initial.keys() != {"ready"} or initial["ready"] is not True:
        raise ConnectorError(ErrorCode.CAPTURE, "The video encoder did not become ready.")
    ready.set()
    return await _report(reader)


class EncoderProcess:
    """Run one isolated worker and reap it on success, failure, or cancellation."""

    def __init__(self, command: Sequence[str], shutdown_seconds: float = 2) -> None:
        self.command = command
        self.shutdown_seconds = shutdown_seconds
        self.process: asyncio.subprocess.Process | None = None

    async def _reap(self) -> None:
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
                    "The encoder process did not stop. Restart ComfyUI before another run.",
                ) from None

    async def _dispose(self, tasks: Sequence[asyncio.Task[object]]) -> None:
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
        feed: Callable[[asyncio.StreamWriter], Coroutine[object, object, None]],
        ready: asyncio.Event,
        stopped: asyncio.Event,
    ) -> dict[str, Json]:
        """Observe input, result, and stop signals without blocking the host loop."""
        environment = {
            key: value for key, value in os.environ.items() if not key.startswith("REACTOR_")
        }
        self.process = await asyncio.create_subprocess_exec(
            *self.command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
            env=environment,
            limit=4096,
        )
        tasks: list[asyncio.Task[object]] = []
        try:
            if self.process.stdin is None or self.process.stdout is None:
                raise ConnectorError(ErrorCode.CAPTURE, "The video encoder pipes are unavailable.")
            feeder = asyncio.create_task(feed(self.process.stdin))
            reader = asyncio.create_task(_read_result(self.process.stdout, ready))
            interrupted = asyncio.create_task(stopped.wait())
            tasks.extend((feeder, reader, interrupted))
            completed, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            if feeder in completed:
                await feeder
                await asyncio.wait({reader, interrupted}, return_when=asyncio.FIRST_COMPLETED)
            if interrupted.done():
                raise ConnectorError(ErrorCode.CAPTURE, "Video capture was stopped.")
            result = await reader
            async with asyncio.timeout(self.shutdown_seconds):
                returncode = await self.process.wait()
            if returncode != 0:
                raise ConnectorError(ErrorCode.CAPTURE, ENCODER_ERRORS["encoder_failed"])
            return result
        finally:
            cleanup = asyncio.create_task(self._dispose(tasks))
            cancelled = False
            while not cleanup.done():
                try:
                    await asyncio.shield(cleanup)
                except asyncio.CancelledError:
                    cancelled = True
                except Exception:
                    break
            if cancelled:
                if not cleanup.cancelled():
                    cleanup.exception()
                raise asyncio.CancelledError
            cleanup.result()
