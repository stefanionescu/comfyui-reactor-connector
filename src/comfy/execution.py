"""Apply private settings and ComfyUI cancellation to model execution."""

import sys
import asyncio
from pathlib import Path
import tempfile
from functools import partial
from contextlib import asynccontextmanager
from collections.abc import Callable, Awaitable, AsyncGenerator

import folder_paths
from comfy_api.latest import ComfyAPI, InputImpl, io
from comfy.model_management import InterruptProcessingException, throw_exception_if_processing_interrupted

from ..errors import ErrorCode, ConnectorError
from ..runtime import get_runtime
from .interaction import prepare_interaction
from ..media.audio import read_audio
from ..state.media import CaptureResult
from ..live.options import LiveOptions
from ..media.output import owned_io, discard_outputs
from ..state.session import SessionOutcome
from ..state.settings import ExecutionConfiguration
from ..execution.inputs import VideoOperation
from ..live.interaction import LiveInteraction
from ..config.media.capture import MAX_QUEUE_BYTES
from ..execution.interaction import SessionInteraction
from ..config.messages.session import RUN_TIMEOUT
from ..config.generation.session import CANCELLATION_POLL_SECONDS
from ..execution.session.capture import capture_video


async def _run_session(
    operation: VideoOperation,
    configuration: ExecutionConfiguration,
    destination: Path,
    open_interaction: Callable[[], Awaitable[LiveInteraction | None]],
) -> CaptureResult:
    """Own live controls and remote cleanup.

    Args:
        operation: The model operation to run.
        configuration: The settings and the key for this run.
        destination: The path that receives the recording.
        open_interaction: The call that opens the live controls, or returns None without them.

    Returns:
        The captured recording.

    """
    outcome = SessionOutcome()
    interaction = None
    try:
        interaction = await open_interaction()
        hooks = None
        if interaction is not None:
            lease = interaction.lease
            hooks = SessionInteraction(
                interaction.connected,
                lease.enable_controls,
                interaction.stop,
                lambda is_confirmed, failed: lease.close(is_termination_confirmed=is_confirmed, failed=failed),
            )
        return await capture_video(
            operation,
            configuration,
            destination,
            outcome=outcome,
            interaction=hooks,
        )
    finally:
        if interaction is not None:
            interaction.lease.close(
                is_termination_confirmed=outcome.is_termination_confirmed,
                failed=sys.exception() is not None,
            )


@asynccontextmanager
async def _temporary_video() -> AsyncGenerator[Path, None]:
    """Reserve a recording path off the event loop and remove incomplete output.

    Yields:
        The path of the reserved recording.

    """
    destination: Path | None = None

    def reserve_destination() -> Path:
        """Retain the path so cancellation can remove it after file creation finishes.

        Returns:
            The path of the new temporary file.

        """
        nonlocal destination
        with tempfile.NamedTemporaryFile(
            prefix='reactor-', suffix='.mp4', dir=folder_paths.get_temp_directory(), delete=False
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
            await discard_outputs(destination, destination.with_suffix('.wav'), error=sys.exception())


async def wait_for_execution[T](task: asyncio.Task[T]) -> T:
    """Forward ComfyUI interruption to the owned preparation or execution task.

    Args:
        task: The task to wait for, which is cancelled on interruption.

    Returns:
        The result of the task.

    """
    try:
        while not task.done():
            throw_exception_if_processing_interrupted()
            await asyncio.wait({task}, timeout=CANCELLATION_POLL_SECONDS)
        return await task
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)


async def node_output(result: CaptureResult) -> io.NodeOutput:
    """Create native ComfyUI outputs and release temporary audio after loading its samples.

    Args:
        result: The captured recording and its optional sound file.

    Returns:
        The video output, with the sound when the recording has one.

    """
    if result.audio_path is not None:
        audio_path = result.audio_path
        try:
            audio = await owned_io(lambda: read_audio(audio_path, MAX_QUEUE_BYTES))
        finally:
            await discard_outputs(audio_path, error=sys.exception())
        return io.NodeOutput(InputImpl.VideoFromFile(str(result.path)), audio)
    return io.NodeOutput(InputImpl.VideoFromFile(str(result.path)))


async def generate_video(
    operation: VideoOperation,
    *,
    interactive: bool = False,
    controls: LiveOptions | None = None,
) -> io.NodeOutput:
    """Return a native video only after encoding and remote cleanup succeed.

    Args:
        operation: The model operation to run.
        interactive: Whether to open the live controls of the model.
        controls: The live options to use, or None to build them from the operation.

    Returns:
        The video output of the node.

    Raises:
        ConnectorError: When the run fails or times out.
        InterruptProcessingException: When the user interrupts the run.

    """
    progress = ComfyAPI().execution
    await progress.set_progress(0, 3)
    configuration = await asyncio.to_thread(get_runtime().configuration.read_execution_configuration)
    operation.validate(configuration.settings)
    await progress.set_progress(1, 3)
    try:
        async with _temporary_video() as destination:
            task = asyncio.create_task(
                _run_session(
                    operation,
                    configuration,
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
