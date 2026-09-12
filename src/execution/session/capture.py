"""Run a model and encoder within the configured recording and session limits."""

import sys
import json
import asyncio
from pathlib import Path
from ...language import translate
from ..failures import safe_error
from ..events import SessionEvents
from ..cleanup import finish_session
from ..operation import VideoOperation
from .resources import SessionResources
from ...state.media import CaptureResult
from ...media.capture import VideoCapture
from ...state.reports import FailureReport
from ..diagnostics import describe_failure
from ...media.output import discard_outputs
from ..interaction import SessionInteraction
from ...errors import ErrorCode, ConnectorError
from ...state.settings import ExecutionConfiguration
from ...media.units import convert_mebibytes_to_bytes
from ...media.recording.assemble import prepare_recording
from ..transport import Track, Transport, SessionTransport
from ...state.session import SessionOutcome, RecordingWindow
from ....config.generation.session import CAPTURE_DRAIN_SECONDS


def _video_track(transport: Transport) -> Track:
    """Require exactly one receive-only main video track."""
    tracks = [
        track
        for track in transport.tracks
        if track.name == "main_video" and track.kind == "video" and track.direction == "recvonly"
    ]
    if len(tracks) != 1:
        raise ConnectorError(ErrorCode.UNAVAILABLE, translate("main", "errors.videoTrackMissing"))
    return tracks[0]


async def _capture_generation(session: SessionResources) -> tuple[CaptureResult, RecordingWindow]:
    """Connect, configure the model, and capture the requested video and recording."""
    recording_window = RecordingWindow(0, session.operation.duration_seconds)
    await session.capture.ready.wait()
    if session.worker.done():
        return await session.worker, recording_window
    async with asyncio.timeout(session.settings.connect_timeout_seconds):
        session.outcome.is_connection_attempted = True
        await session.events.call("connect", session.transport.connect())
    session.events.check()
    track = _video_track(session.transport)
    session.track = track
    track.on_frame(session.capture.receive)
    if session.interaction is not None:
        await session.interaction.connected(session.transport, track, session.events)
    recording_window = await session.operation.begin_generation(
        session.transport,
        session.events,
        session.settings.max_capture_seconds,
    )
    if session.interaction is not None:
        session.interaction.configured(video_started=session.capture.first_frame.is_set())
    session.events.phase = "capture"
    async with asyncio.timeout(session.settings.first_frame_timeout_seconds):
        await session.capture.first_frame.wait()
    if session.operation.requires_audio:
        # Generation can finish before WebRTC delivers the requested recorded interval.
        await session.capture.complete.wait()
    else:
        await _capture_until_end(session.capture, session.events)
    result = await asyncio.shield(session.worker)
    session.events.capture_frames = result.frames
    if session.operation.requires_audio:
        await session.events.call(
            "recording",
            session.transport.save_recording(
                session.capture.path.with_suffix(".recording.mp4"),
                maximum_bytes=convert_mebibytes_to_bytes(session.settings.max_capture_megabytes),
                timeout_seconds=session.settings.max_session_seconds,
                on_window=session.events.on_recording_window,
            ),
        )
    return result, recording_window


async def _capture_until_end(capture: VideoCapture, events: SessionEvents) -> None:
    """Bound the final delivery drain when a finite model reports completion."""
    captured = asyncio.create_task(capture.complete.wait())
    completed = asyncio.create_task(events.generation_complete.wait())
    try:
        await asyncio.wait({captured, completed}, return_when=asyncio.FIRST_COMPLETED)
        if completed.done() and not captured.done():
            # Model messages and video use separate channels. Allow in-flight
            # frames to arrive, then close without recording a frozen final frame forever.
            try:
                await asyncio.wait_for(asyncio.shield(captured), CAPTURE_DRAIN_SECONDS)
            except TimeoutError:
                capture.finish()
            await asyncio.gather(captured)
    finally:
        for task in (captured, completed):
            if not task.done():
                task.cancel()
        await asyncio.gather(captured, completed, return_exceptions=True)


def session_failure(events: SessionEvents, error: BaseException | None) -> FailureReport | None:
    """Record the failed operation without replacing its execution error."""
    diagnostic = events.diagnostic
    if diagnostic is None and isinstance(error, ConnectorError):
        diagnostic = describe_failure(events.phase, error)
    if diagnostic is None and isinstance(error, TimeoutError):
        diagnostic = FailureReport(
            events.phase,
            "timeout",
            json.dumps(
                {
                    "reason": translate("main", "errors.sessionDeadline"),
                    "state_received": events.state_ready.is_set(),
                    "message_types": sorted(events.message_types),
                    "capture_frames": events.capture_frames,
                    "recording_window": events.recording_window,
                    "model_timing": events.model_timing,
                }
            ),
        )
    return diagnostic


async def _capture_session(session: SessionResources) -> tuple[CaptureResult, RecordingWindow]:
    """Own capture and event listeners through generation, failure, and cleanup."""
    try:
        session.events.attach()
        async with asyncio.timeout(session.settings.max_session_seconds):
            return await session.events.guard(_capture_generation(session))
    finally:
        session.outcome.diagnostic = session_failure(session.events, sys.exception())
        await finish_session(session, sys.exception())


async def capture_video(
    operation: VideoOperation,
    configuration: ExecutionConfiguration,
    destination: Path,
    *,
    outcome: SessionOutcome,
    interaction: SessionInteraction | None = None,
) -> CaptureResult:
    """Capture an already validated operation and clean up every outcome."""
    settings = configuration.settings
    capture = VideoCapture(
        destination,
        operation.duration_seconds,
        convert_mebibytes_to_bytes(settings.max_queue_megabytes),
        convert_mebibytes_to_bytes(settings.max_capture_megabytes),
        fallback_fps=operation.fallback_fps,
    )
    try:
        transport = SessionTransport(operation.connection_name, configuration.credential, settings.max_session_seconds)
        events = SessionEvents(transport)
        session = SessionResources(
            operation=operation,
            transport=transport,
            settings=settings,
            capture=capture,
            events=events,
            worker=asyncio.create_task(capture.encode()),
            outcome=outcome,
            interaction=interaction,
        )
        result, recording_window = await _capture_session(session)
        if operation.requires_audio:
            result = await prepare_recording(
                destination.with_suffix(".recording.mp4"),
                destination,
                recording_window.duration_seconds,
                settings,
                start_seconds=recording_window.start_seconds,
            )
    except asyncio.CancelledError:
        raise
    except Exception as error:  # noqa: BLE001 -- reason: Translate SDK and native media failures at the public execution boundary.
        raise safe_error(error) from None
    else:
        return result
    finally:
        error = sys.exception()
        discarded: list[Path] = []
        if operation.requires_audio:
            discarded.append(destination.with_suffix(".recording.mp4"))
        if error is not None:
            discarded.extend((destination, destination.with_suffix(".wav")))
        if discarded:
            await discard_outputs(*discarded, error=error)
