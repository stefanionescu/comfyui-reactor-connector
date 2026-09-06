"""Run a model and encoder within the configured recording and session limits."""

import asyncio
import json
import sys
from collections.abc import Callable
from pathlib import Path

from ..config import Settings
from ..credentials import Credential
from ..errors import ConnectorError, ErrorCode
from ..media.capture import CaptureResult, VideoCapture
from ..media.file_output import owned_io
from ..media.recording import prepare_recording
from .cleanup import finish_session
from .diagnostics import FailureDetails
from .events import SessionEvents
from .helios import HeliosRequest as HeliosRequest
from .interaction import SessionInteraction
from .operation import VideoOperation
from .outcome import SessionOutcome
from .sdk_errors import safe_error
from .transport import Track, Transport, create_transport


def _video_track(transport: Transport) -> Track:
    tracks = [
        track
        for track in transport.tracks
        if track.name == "main_video" and track.kind == "video" and track.direction == "recvonly"
    ]
    if len(tracks) != 1:
        raise ConnectorError(
            ErrorCode.UNAVAILABLE, "The model did not declare its expected video track."
        )
    return tracks[0]


async def _generate(
    transport: Transport,
    request: VideoOperation,
    settings: Settings,
    capture: VideoCapture,
    worker: asyncio.Task[CaptureResult],
    receivers: list[Track],
    events: SessionEvents,
    outcome: SessionOutcome,
    interaction: SessionInteraction | None,
) -> CaptureResult:
    await capture.ready.wait()
    if worker.done():
        return await worker
    async with asyncio.timeout(settings.connect_timeout_seconds):
        outcome.connection_attempted = True
        await events.call("connect", transport.connect())
    events.check()
    track = _video_track(transport)
    receivers.append(track)
    track.on_frame(capture.receive)
    if interaction is not None:
        await interaction.connected(transport, track, events)
    await request.configure(transport, events)
    if interaction is not None:
        interaction.configured(video_started=capture.first_frame.is_set())
    events.phase = "capture"
    async with asyncio.timeout(settings.first_frame_timeout_seconds):
        await capture.first_frame.wait()
    if request.requires_audio:
        # Generation can finish before WebRTC delivers the requested recorded interval.
        await capture.complete.wait()
    else:
        await _capture_until_end(capture, events)
    result = await asyncio.shield(worker)
    events.capture_frames = result.frames
    if request.requires_audio:
        await events.call(
            "recording",
            transport.save_recording(
                capture.path.with_suffix(".recording.mp4"),
                maximum_bytes=settings.max_capture_megabytes * 1_048_576,
                timeout_seconds=settings.max_session_seconds,
                on_window=events.on_recording_window,
            ),
        )
    return result


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
                await asyncio.wait_for(asyncio.shield(captured), 0.5)
            except TimeoutError:
                capture.finish()
            await captured
    finally:
        for task in (captured, completed):
            if not task.done():
                task.cancel()
        await asyncio.gather(captured, completed, return_exceptions=True)


async def _run(
    transport: Transport,
    request: VideoOperation,
    settings: Settings,
    capture: VideoCapture,
    outcome: SessionOutcome,
    interaction: SessionInteraction | None,
) -> CaptureResult:
    worker = asyncio.create_task(capture.encode())
    events = SessionEvents(transport)
    receivers: list[Track] = []
    try:
        events.attach()
        async with asyncio.timeout(settings.max_session_seconds):
            return await events.guard(
                _generate(
                    transport,
                    request,
                    settings,
                    capture,
                    worker,
                    receivers,
                    events,
                    outcome,
                    interaction,
                )
            )
    finally:
        diagnostic = events.diagnostic
        error = sys.exception()
        if diagnostic is None and isinstance(error, ConnectorError):
            diagnostic = FailureDetails.from_error(events.phase, error)
        if diagnostic is None and isinstance(sys.exception(), TimeoutError):
            diagnostic = FailureDetails(
                events.phase,
                "timeout",
                json.dumps(
                    {
                        "reason": "The session deadline expired during this operation.",
                        "state_received": events.state_ready.is_set(),
                        "message_types": sorted(events.message_types),
                        "capture_frames": events.capture_frames,
                        "recording_window": events.recording_window,
                        "model_timing": events.model_timing,
                    }
                ),
            )
        outcome.diagnostic = diagnostic
        track = receivers[0] if receivers else None
        await finish_session(
            transport,
            settings,
            capture,
            worker,
            events,
            track,
            sys.exception(),
            outcome,
            release_controls=lambda: request.release(transport),
            interaction=interaction,
        )


async def run_video(
    request: VideoOperation,
    credential: Credential,
    settings: Settings,
    destination: Path,
    *,
    transport_factory: Callable[[str, Credential, int], Transport] = create_transport,
    outcome: SessionOutcome | None = None,
    interaction: SessionInteraction | None = None,
) -> CaptureResult:
    """Validate before billing and clean up after every execution outcome."""
    request.validate(settings)
    capture = VideoCapture(
        destination,
        request.duration_seconds,
        settings.max_queue_megabytes * 1_048_576,
        settings.max_capture_megabytes * 1_048_576,
        fallback_fps=request.fallback_fps,
    )
    try:
        transport = transport_factory(request.model_name, credential, settings.max_session_seconds)
        result = await _run(
            transport, request, settings, capture, outcome or SessionOutcome(), interaction
        )
        if request.requires_audio:
            result = await prepare_recording(
                destination.with_suffix(".recording.mp4"),
                destination,
                destination.with_suffix(".wav"),
                request.recording_duration_seconds,
                settings,
                start_seconds=request.recording_start_seconds,
            )
        return result
    except asyncio.CancelledError:
        raise
    except Exception as error:
        raise safe_error(error) from None
    finally:
        if request.requires_audio:
            await owned_io(
                lambda: destination.with_suffix(".recording.mp4").unlink(missing_ok=True)
            )
        if sys.exception() is not None:
            await owned_io(lambda: destination.unlink(missing_ok=True))
            await owned_io(lambda: destination.with_suffix(".wav").unlink(missing_ok=True))


run_helios = run_video
