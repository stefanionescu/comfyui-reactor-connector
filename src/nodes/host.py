"""Apply private settings and ComfyUI cancellation to model execution."""

import sys
import json
import asyncio
import tempfile
import folder_paths
from pathlib import Path
from ..codes import ErrorCode
from functools import partial
from contextlib import suppress
from ..serialization import Json
from ..runtime import get_runtime
from ..errors import ConnectorError
from ..media.output import owned_io
from ..media.audio import read_audio
from ..execution.report import RunReport
from ..settings.settings import Settings
from ..media.capture import CaptureResult
from ..settings.store import read_settings
from comfy_api.latest import io, InputImpl
from ..live.control.lease import LiveOptions
from .interaction import prepare_interaction
from ..execution.session.run import run_video
from ..execution.outcome import SessionOutcome
from collections.abc import Callable, Awaitable
from ..execution.diagnostics import save_failure
from ..execution.operation import VideoOperation
from ..live.interaction import CameraInteraction
from ..media.metadata.read import read_recording
from ..settings.execution import ExecutionConfiguration
from ..execution.session.reservation import SessionReservation
from comfy.model_management import InterruptProcessingException, throw_exception_if_processing_interrupted


async def wait_for_execution[T](task: asyncio.Task[T]) -> T:
    """Forward ComfyUI interruption to the owned preparation or execution task."""
    try:
        while not task.done():
            throw_exception_if_processing_interrupted()
            await asyncio.wait({task}, timeout=0.1)
        return await task
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)


async def _admitted_run(
    request: VideoOperation,
    configuration: ExecutionConfiguration,
    destination: Path,
    report: RunReport,
    open_interaction: Callable[[], Awaitable[CameraInteraction | None]],
) -> tuple[CaptureResult, dict[str, Json] | None]:
    """Own admission, live controls, remote cleanup, and private failure diagnostics."""
    settings = configuration.settings
    admission = get_runtime().sessions
    async with admission.slot(settings.queue_timeout_seconds):
        outcome = SessionOutcome()
        interaction = None
        try:
            interaction = await open_interaction()
            # A connection may start near the end of local setup. Keep the record
            # for that window plus the full remote session limit and cleanup.
            reservation = SessionReservation(
                get_runtime().configuration.directory,
                2 * settings.max_session_seconds + settings.cleanup_timeout_seconds,
            )
            async with reservation.protect(outcome):
                result = await run_video(
                    request,
                    configuration,
                    destination,
                    outcome=outcome,
                    interaction=interaction,
                )
            return result, interaction.summary() if interaction is not None else None
        finally:
            if interaction is not None:
                interaction.closed(
                    termination_confirmed=outcome.termination_confirmed,
                    failed=sys.exception() is not None,
                )
            if outcome.termination_uncertain:
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
    settings: Settings,
    interaction_summary: dict[str, Json] | None,
) -> str:
    """Combine saved media facts with the execution and live-control report."""
    facts = report.to_json()
    recording = await wait_for_execution(
        asyncio.create_task(read_recording(result, settings.max_capture_megabytes * 1_048_576))
    )
    facts.update(recording)
    if interaction_summary is not None:
        facts["live"] = interaction_summary
    return json.dumps(facts)


async def node_output(
    result: CaptureResult,
    metadata: str,
    settings: Settings,
    interaction_summary: dict[str, Json] | None,
) -> io.NodeOutput:
    """Create native ComfyUI outputs and release temporary audio after loading its samples."""
    if result.audio_path is not None:
        audio_path = result.audio_path
        try:
            audio = await owned_io(lambda: read_audio(audio_path, settings.max_queue_megabytes * 1_048_576))
        finally:
            await owned_io(partial(audio_path.unlink, missing_ok=True))
        return io.NodeOutput(InputImpl.VideoFromFile(str(result.path)), audio, metadata)
    video = InputImpl.VideoFromFile(str(result.path))
    if interaction_summary is not None:
        return io.NodeOutput(video, metadata, ui={"reactor_live": [interaction_summary]})
    return io.NodeOutput(video, metadata)


async def execute_video(
    request: VideoOperation,
    *,
    node_id: str,
    interactive: bool = False,
    controls: LiveOptions | None = None,
) -> io.NodeOutput:
    """Return a native video only after encoding and remote cleanup succeed."""
    if type(interactive) is not bool:
        raise ConnectorError(ErrorCode.INVALID_INPUT, "Choose whether live controls are enabled.")
    configuration = get_runtime().configuration
    request.validate(await asyncio.to_thread(read_settings, configuration.directory))
    snapshot = await asyncio.to_thread(configuration.execution_snapshot)
    request.validate(snapshot.settings)
    report = await owned_io(lambda: RunReport.prepare(node_id, request.model_name, request.duration_seconds))
    with tempfile.NamedTemporaryFile(
        prefix="reactor-",
        suffix=".mp4",
        dir=folder_paths.get_temp_directory(),
        delete=False,
    ) as temporary:
        destination = Path(temporary.name)
    success = False
    try:
        task = asyncio.create_task(
            _admitted_run(
                request,
                snapshot,
                destination,
                report,
                partial(prepare_interaction, request, interactive=interactive, controls=controls),
            )
        )
        result, interaction_summary = await wait_for_execution(task)
        metadata = await recording_report(report, result, snapshot.settings, interaction_summary)
        output = await node_output(result, metadata, snapshot.settings, interaction_summary)
    except ConnectorError as error:
        if error.code == ErrorCode.INTERRUPTED:
            raise InterruptProcessingException from None
        raise
    except TimeoutError:
        raise ConnectorError(ErrorCode.TIMEOUT, "Reactor did not finish within the configured time limit.") from None
    else:
        success = True
        return output
    finally:
        if not success:
            await asyncio.to_thread(destination.unlink, missing_ok=True)
            await owned_io(partial(destination.with_suffix(".wav").unlink, missing_ok=True))


async def operation_fingerprint(contract: str) -> str:
    """Include the adapter revision and private execution generation in the cache key."""
    snapshot = await asyncio.to_thread(get_runtime().configuration.execution_snapshot)
    return f"{contract}:{snapshot.generation}"
