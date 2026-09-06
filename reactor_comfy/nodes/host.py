"""Apply private settings and ComfyUI cancellation to model execution."""

import asyncio
import json
import os
import sys
import tempfile
from contextlib import suppress
from pathlib import Path

import folder_paths
from comfy.model_management import (
    InterruptProcessingException,
    throw_exception_if_processing_interrupted,
)
from comfy_api.latest import InputImpl, io

from ..config import Settings
from ..config_store import load_settings
from ..credentials import Credential
from ..errors import ConnectorError, ErrorCode
from ..execution.diagnostics import save_failure
from ..execution.operation import VideoOperation
from ..execution.outcome import SessionOutcome
from ..execution.report import RunReport
from ..execution.session import run_video
from ..execution.session_guard import SessionReservation
from ..execution.visko import ViskoStableRequest
from ..json_data import Json
from ..live.control_lease import LiveOptions
from ..media.audio import load_audio
from ..media.capture import CaptureResult
from ..media.file_output import owned_io
from ..media.metadata import recording_details
from ..runtime import get_runtime
from .interaction import prepare_camera, prepare_controls


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
    credential: Credential,
    settings: Settings,
    destination: Path,
    interactive: bool,
    controls: LiveOptions | None,
    report: RunReport,
) -> tuple[CaptureResult, dict[str, Json] | None]:
    admission = get_runtime().sessions
    async with admission.slot(settings.queue_timeout_seconds):
        outcome = SessionOutcome()
        interaction = None
        try:
            if controls is not None:
                interaction = await prepare_controls(controls, request.duration_seconds)
            elif interactive:
                if request.model_name in ("reactor/lingbot", "reactor/lingbot-world-2"):
                    interaction = await prepare_camera(
                        request.model_name, request.prompt, request.duration_seconds
                    )
                else:
                    options = LiveOptions(
                        request.model_name,
                        request.prompt,
                        passthrough=request.prompt_passthrough
                        if isinstance(request, ViskoStableRequest)
                        else False,
                        audio_prompt=request.audio_prompt
                        if isinstance(request, ViskoStableRequest)
                        else "",
                        audio_enabled=request.audio_enabled
                        if isinstance(request, ViskoStableRequest)
                        else False,
                    )
                    interaction = await prepare_controls(options, request.duration_seconds)
            # A connection may start near the end of local setup. Keep the record
            # for that window plus the full remote session limit and cleanup.
            reservation = SessionReservation(
                get_runtime().configuration.directory,
                2 * settings.max_session_seconds + settings.cleanup_timeout_seconds,
            )
            async with reservation.protect(outcome):
                result = await run_video(
                    request,
                    credential,
                    settings,
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
                        lambda: save_failure(
                            get_runtime().configuration.directory,
                            diagnostic,
                            credential,
                            run_id=report.run_id,
                        )
                    )


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
    directory = configuration.directory
    settings = await asyncio.to_thread(load_settings, directory)
    request.validate(settings)
    snapshot = await asyncio.to_thread(configuration.execution_snapshot)
    settings = snapshot.settings
    request.validate(settings)
    credential = snapshot.credential
    report = await owned_io(
        lambda: RunReport.prepare(node_id, request.model_name, request.duration_seconds)
    )
    descriptor, name = tempfile.mkstemp(
        prefix="reactor-",
        suffix=".mp4",
        dir=folder_paths.get_temp_directory(),
    )
    os.close(descriptor)
    destination = Path(name)
    success = False
    try:
        task = asyncio.create_task(
            _admitted_run(request, credential, settings, destination, interactive, controls, report)
        )
        result, interaction_summary = await wait_for_execution(task)
        facts = report.to_json()
        details = await wait_for_execution(
            asyncio.create_task(
                recording_details(result, settings.max_capture_megabytes * 1_048_576)
            )
        )
        facts.update(details)
        if interaction_summary is not None:
            facts["live"] = interaction_summary
        metadata = json.dumps(facts)
        if result.audio_path is not None:
            audio_path = result.audio_path
            try:
                audio = await owned_io(
                    lambda: load_audio(audio_path, settings.max_queue_megabytes * 1_048_576)
                )
            finally:
                await owned_io(lambda: audio_path.unlink(missing_ok=True))
            success = True
            return io.NodeOutput(InputImpl.VideoFromFile(str(result.path)), audio, metadata)
        success = True
        return io.NodeOutput(
            InputImpl.VideoFromFile(str(result.path)),
            metadata,
            ui={"reactor_live": [interaction_summary]} if interaction_summary is not None else None,
        )
    except ConnectorError as error:
        if error.code == ErrorCode.INTERRUPTED:
            raise InterruptProcessingException() from None
        raise
    except TimeoutError:
        raise ConnectorError(
            ErrorCode.TIMEOUT, "Reactor did not finish within the configured time limit."
        ) from None
    finally:
        if not success:
            await asyncio.to_thread(destination.unlink, missing_ok=True)
            await owned_io(lambda: destination.with_suffix(".wav").unlink(missing_ok=True))


async def helios_fingerprint() -> str:
    """Extend the host input signature with the adapter and private configuration generation."""
    snapshot = await asyncio.to_thread(get_runtime().configuration.execution_snapshot)
    return f"helios-bounded-v1:{snapshot.generation}"


async def operation_fingerprint(contract: str) -> str:
    """Include the adapter revision and private execution generation in the cache key."""
    snapshot = await asyncio.to_thread(get_runtime().configuration.execution_snapshot)
    return f"{contract}:{snapshot.generation}"


execute_helios = execute_video
