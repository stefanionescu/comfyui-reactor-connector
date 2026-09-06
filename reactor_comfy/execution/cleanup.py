"""Finish owned cleanup despite repeated host cancellation requests."""

import asyncio
import logging
import sys
from collections.abc import Awaitable, Callable

from ..config import Settings
from ..errors import ConnectorError, ErrorCode
from ..media.capture import CaptureResult, VideoCapture
from .events import SessionEvents
from .interaction import SessionInteraction
from .outcome import SessionOutcome
from .transport import Track, Transport


async def _release(
    transport: Transport,
    settings: Settings,
    capture: VideoCapture,
    worker: asyncio.Task[CaptureResult],
    events: SessionEvents,
    track: Track | None,
    outcome: SessionOutcome,
    release_controls: Callable[[], Awaitable[None]] | None,
    interaction: SessionInteraction | None,
    failed: bool,
) -> None:
    try:
        try:
            if interaction is not None:
                await interaction.stop()
            events.close()
            if track is not None:
                track.off_frame(capture.receive)
        finally:
            try:
                try:
                    if release_controls is not None:
                        async with asyncio.timeout(settings.cleanup_timeout_seconds):
                            await release_controls()
                finally:
                    async with asyncio.timeout(settings.cleanup_timeout_seconds):
                        await transport.disconnect()
                        outcome.termination_confirmed = True
            finally:
                transport.close()
    finally:
        if interaction is not None:
            interaction.closed(
                termination_confirmed=outcome.termination_confirmed,
                failed=failed or sys.exception() is not None,
            )
        # The capture owner terminates and reaps its child before this task completes.
        await asyncio.gather(worker, return_exceptions=True)


async def finish_session(
    transport: Transport,
    settings: Settings,
    capture: VideoCapture,
    worker: asyncio.Task[CaptureResult],
    events: SessionEvents,
    track: Track | None,
    primary_error: BaseException | None,
    outcome: SessionOutcome,
    *,
    release_controls: Callable[[], Awaitable[None]] | None = None,
    interaction: SessionInteraction | None = None,
) -> None:
    """Preserve the original failure and await one cleanup task exactly once."""
    capture.stop()
    cleanup = asyncio.create_task(
        _release(
            transport,
            settings,
            capture,
            worker,
            events,
            track,
            outcome,
            release_controls,
            interaction,
            primary_error is not None,
        )
    )
    cancelled = False
    while not cleanup.done():
        try:
            await asyncio.shield(cleanup)
        except asyncio.CancelledError:
            cancelled = True
        except Exception:
            break
    error = cleanup.exception()
    if error is not None:
        message = (
            "Session cleanup failed; termination is unconfirmed. The server lifetime cap applies."
            if outcome.termination_uncertain
            else "The remote session ended, but local cleanup failed."
        )
        logging.getLogger(__name__).error(message)
    if cancelled:
        raise asyncio.CancelledError
    if error is not None and primary_error is None:
        raise ConnectorError(
            ErrorCode.CLEANUP,
            "Session termination is unconfirmed. Wait for its server limit before retrying."
            if outcome.termination_uncertain
            else "The remote session ended, but local cleanup failed. Restart ComfyUI.",
        ) from None
