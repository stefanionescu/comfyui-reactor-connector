"""Apply private settings and ComfyUI cancellation to model execution."""

import sys
import asyncio
import tempfile
import folder_paths
from pathlib import Path
from functools import partial
from ..runtime import get_runtime
from ..media.audio import read_audio
from ..live.options import LiveOptions
from ..state.media import CaptureResult
from ..state.session import SessionOutcome
from contextlib import asynccontextmanager
from .interaction import prepare_interaction
from ..errors import ErrorCode, ConnectorError
from ..live.interaction import LiveInteraction
from ..execution.operation import VideoOperation
from ..config.messages.session import RUN_TIMEOUT
from ..config.media.capture import MAX_QUEUE_BYTES
from ..state.settings import ExecutionConfiguration
from ..media.output import owned_io, discard_outputs
from comfy_api.latest import io, ComfyAPI, InputImpl
from ..execution.session.capture import capture_video
from collections.abc import Callable, Awaitable, AsyncGenerator
from ..config.generation.session import CANCELLATION_POLL_SECONDS
from comfy.model_management import InterruptProcessingException, throw_exception_if_processing_interrupted


async def wait_for_execution[T](task: asyncio.Task[T]) -> T:
    """Forward ComfyUI interruption to the owned preparation or execution task."""
    try:
        while not task.done():
            throw_exception_if_processing_interrupted()
            await asyncio.wait({task}, timeout=CANCELLATION_POLL_SECONDS)
        return await task
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)


async def _run_session(
    operation: VideoOperation,
    configuration: ExecutionConfiguration,
    destination: Path,
    open_interaction: Callable[[], Awaitable[LiveInteraction | None]],
) -> CaptureResult:
    """Own live controls and remote cleanup."""
    outcome = SessionOutcome()
    interaction = None
    try:
        interaction = await open_interaction()
        return await capture_video(
            operation,
            configuration,
            destination,
            outcome=outcome,
            interaction=interaction,
        )
    finally:
        if interaction is not None:
            interaction.closed(
                is_termination_confirmed=outcome.is_termination_confirmed,
                failed=sys.exception() is not None,
            )


async def node_output(result: CaptureResult) -> io.NodeOutput:
    """Create native ComfyUI outputs and release temporary audio after loading its samples."""
    if result.audio_path is not None:
        audio_path = result.audio_path
        try:
            audio = await owned_io(lambda: read_audio(audio_path, MAX_QUEUE_BYTES))
        finally:
            await discard_outputs(audio_path, error=sys.exception())
        return io.NodeOutput(InputImpl.VideoFromFile(str(result.path)), audio)
    return io.NodeOutput(InputImpl.VideoFromFile(str(result.path)))


@asynccontextmanager
async def _temporary_video() -> AsyncGenerator[Path, None]:
    """Reserve a recording path off the event loop and remove incomplete output."""
    destination: Path | None = None

    def reserve_destination() -> Path:
        """Retain the path so cancellation can remove it after file creation finishes."""
        nonlocal destination
        with tempfile.NamedTemporaryFile(
            prefix="reactor-", suffix=".mp4", dir=folder_paths.get_temp_directory(), delete=False
        ) as temporary:
            destination = Path(temporary.name)
        return destination

    is_complete = False
    try:
        destination = await owned_io(reserve_destination)
        yield destination
        is_complete = True
    finally:
        if not is_complete and destination is not None:
            await discard_outputs(destination, destination.with_suffix(".wav"), error=sys.exception())


async def generate_video(
    operation: VideoOperation,
    *,
    interactive: bool = False,
    controls: LiveOptions | None = None,
) -> io.NodeOutput:
    """Return a native video only after encoding and remote cleanup succeed."""
    progress = ComfyAPI().execution
    await progress.set_progress(0, 3)
    configuration = get_runtime().configuration
    snapshot = await asyncio.to_thread(configuration.execution_snapshot)
    operation.validate(snapshot.settings)
    await progress.set_progress(1, 3)
    try:
        async with _temporary_video() as destination:
            task = asyncio.create_task(
                _run_session(
                    operation,
                    snapshot,
                    destination,
                    partial(prepare_interaction, operation, interactive=interactive, controls=controls),
                )
            )
            result = await wait_for_execution(task)
            await progress.set_progress(2, 3)
            output = await node_output(result)
            await progress.set_progress(3, 3)
            return output
    except ConnectorError as error:
        if error.code == ErrorCode.INTERRUPTED:
            raise InterruptProcessingException from None
        raise
    except TimeoutError:
        raise ConnectorError(ErrorCode.TIMEOUT, RUN_TIMEOUT) from None


async def operation_fingerprint() -> str:
    """Return the token that changes when the key or execution limits change."""
    snapshot = await asyncio.to_thread(get_runtime().configuration.execution_snapshot)
    return snapshot.generation
