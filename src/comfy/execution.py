"""Apply private settings and ComfyUI cancellation to model execution."""

import sys
import json
import asyncio
import tempfile
import folder_paths
from pathlib import Path
from functools import partial
from ..runtime import get_runtime
from ..state.documents import Json
from ..media.audio import read_audio
from ..state.reports import RunReport
from ..live.options import LiveOptions
from ..state.media import CaptureResult
from ..state.session import SessionOutcome
from .interaction import prepare_interaction
from ..execution.report import prepare_report
from ..errors import ErrorCode, ConnectorError
from ..live.interaction import LiveInteraction
from ..execution.diagnostics import save_failure
from ..execution.operation import VideoOperation
from ..config.messages.session import RUN_TIMEOUT
from ..state.settings import ExecutionConfiguration
from ..media.output import owned_io, discard_outputs
from comfy_api.latest import io, ComfyAPI, InputImpl
from contextlib import suppress, asynccontextmanager
from ..execution.session.capture import capture_video
from ..media.metadata.read import read_recording_metadata
from ..execution.session.reservation import SessionReservation
from collections.abc import Callable, Awaitable, AsyncGenerator
from ..config.media.capture import MAX_QUEUE_BYTES, MAX_CAPTURE_BYTES
from comfy.model_management import InterruptProcessingException, throw_exception_if_processing_interrupted
from ..config.generation.session import (
    QUEUE_TIMEOUT_SECONDS,
    CLEANUP_TIMEOUT_SECONDS,
    CANCELLATION_POLL_SECONDS,
)


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


async def _generate_admitted_video(
    operation: VideoOperation,
    configuration: ExecutionConfiguration,
    destination: Path,
    report: RunReport,
    open_interaction: Callable[[], Awaitable[LiveInteraction | None]],
) -> tuple[CaptureResult, dict[str, Json] | None]:
    """Own admission, live controls, remote cleanup, and private failure diagnostics."""
    settings = configuration.settings
    admission = get_runtime().sessions
    async with admission.slot(QUEUE_TIMEOUT_SECONDS):
        outcome = SessionOutcome()
        interaction = None
        try:
            interaction = await open_interaction()
            # A connection may start near the end of local setup. Keep the record
            # for that window plus the full remote session limit and cleanup.
            reservation = SessionReservation(
                get_runtime().configuration.directory,
                2 * settings.max_session_seconds + CLEANUP_TIMEOUT_SECONDS,
            )
            async with reservation.protect(outcome):
                result = await capture_video(
                    operation,
                    configuration,
                    destination,
                    outcome=outcome,
                    interaction=interaction,
                )
            return result, interaction.summary() if interaction is not None else None
        finally:
            if interaction is not None:
                interaction.closed(
                    is_termination_confirmed=outcome.is_termination_confirmed,
                    failed=sys.exception() is not None,
                )
            if outcome.is_termination_uncertain:
                admission.block_for(settings.max_session_seconds)
            diagnostic = outcome.diagnostic
            if diagnostic is not None:
                # Diagnostic storage must not replace the original execution failure.
                with suppress(OSError, ConnectorError):
                    await owned_io(
                        partial(
                            save_failure,
                            get_runtime().configuration.directory,
                            diagnostic,
                            configuration.credential,
                            run_id=report.run_id,
                        )
                    )


async def recording_report(
    report: RunReport,
    result: CaptureResult,
    interaction_summary: dict[str, Json] | None,
) -> str:
    """Combine saved media facts with the execution and live-control report."""
    facts = report.to_json()
    recording = await wait_for_execution(asyncio.create_task(read_recording_metadata(result, MAX_CAPTURE_BYTES)))
    facts.update(recording)
    if interaction_summary is not None:
        facts["live"] = interaction_summary
    return json.dumps(facts)


async def node_output(
    result: CaptureResult,
    metadata: str,
    interaction_summary: dict[str, Json] | None,
) -> io.NodeOutput:
    """Create native ComfyUI outputs and release temporary audio after loading its samples."""
    if result.audio_path is not None:
        audio_path = result.audio_path
        try:
            audio = await owned_io(lambda: read_audio(audio_path, MAX_QUEUE_BYTES))
        finally:
            await discard_outputs(audio_path, error=sys.exception())
        return io.NodeOutput(InputImpl.VideoFromFile(str(result.path)), audio, metadata)
    video = InputImpl.VideoFromFile(str(result.path))
    if interaction_summary is not None:
        return io.NodeOutput(video, metadata, ui={"reactor_live": [interaction_summary]})
    return io.NodeOutput(video, metadata)


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
    node_id: str,
    interactive: bool = False,
    controls: LiveOptions | None = None,
) -> io.NodeOutput:
    """Return a native video only after encoding and remote cleanup succeed."""
    progress = ComfyAPI().execution
    await progress.set_progress(0, 3)
    configuration = get_runtime().configuration
    snapshot = await asyncio.to_thread(configuration.execution_snapshot)
    operation.validate(snapshot.settings)
    report = await owned_io(lambda: prepare_report(node_id, operation.connection_name, operation.duration_seconds))
    await progress.set_progress(1, 3)
    try:
        async with _temporary_video() as destination:
            task = asyncio.create_task(
                _generate_admitted_video(
                    operation,
                    snapshot,
                    destination,
                    report,
                    partial(prepare_interaction, operation, interactive=interactive, controls=controls),
                )
            )
            result, interaction_summary = await wait_for_execution(task)
            await progress.set_progress(2, 3)
            metadata = await recording_report(report, result, interaction_summary)
            output = await node_output(result, metadata, interaction_summary)
            await progress.set_progress(3, 3)
            return output
    except ConnectorError as error:
        if error.code == ErrorCode.INTERRUPTED:
            raise InterruptProcessingException from None
        raise
    except TimeoutError:
        raise ConnectorError(ErrorCode.TIMEOUT, RUN_TIMEOUT) from None


async def operation_fingerprint(contract: str) -> str:
    """Include the adapter revision and private execution generation in the cache key."""
    snapshot = await asyncio.to_thread(get_runtime().configuration.execution_snapshot)
    return f"{contract}:{snapshot.generation}"
