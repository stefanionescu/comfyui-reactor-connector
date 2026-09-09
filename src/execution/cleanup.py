"""Finish owned cleanup despite repeated host cancellation requests."""

import sys
import asyncio
import logging
from ..language import translate
from .session.state import SessionResources
from ..errors import ErrorCode, ConnectorError


async def _release(session: SessionResources, *, failed: bool) -> None:
    """Release controls, disconnect, and reap capture even when an earlier cleanup step fails."""
    try:
        try:
            if session.interaction is not None:
                await session.interaction.stop()
            session.events.close()
            if session.track is not None:
                session.track.off_frame(session.capture.receive)
        finally:
            try:
                try:
                    async with asyncio.timeout(session.settings.cleanup_timeout_seconds):
                        await session.request.release(session.transport)
                finally:
                    async with asyncio.timeout(session.settings.cleanup_timeout_seconds):
                        await session.transport.disconnect()
                        session.outcome.is_termination_confirmed = True
            finally:
                session.transport.close()
    finally:
        if session.interaction is not None:
            session.interaction.closed(
                is_termination_confirmed=session.outcome.is_termination_confirmed,
                failed=failed or sys.exception() is not None,
            )
        # The capture owner terminates and reaps its child before this task completes.
        await asyncio.gather(session.worker, return_exceptions=True)


async def finish_session(session: SessionResources, primary_error: BaseException | None) -> None:
    """Preserve the original failure and await one cleanup task exactly once."""
    session.capture.stop()
    cleanup = asyncio.create_task(_release(session, failed=primary_error is not None))
    cancelled = False
    while not cleanup.done():
        try:
            await asyncio.shield(cleanup)
        except asyncio.CancelledError:
            cancelled = True
        except Exception:  # noqa: BLE001 -- reason: Inspect the completed cleanup task below without losing a pending cancellation.
            break
    error = cleanup.exception()
    if error is not None:
        message = (
            translate("main", "errors.cleanupUnconfirmed")
            if session.outcome.is_termination_uncertain
            else translate("main", "errors.localCleanupFailed")
        )
        logging.getLogger(__name__).error(message)
    if cancelled:
        raise asyncio.CancelledError
    if error is not None and primary_error is None:
        raise ConnectorError(
            ErrorCode.CLEANUP,
            translate("main", "errors.terminationUnconfirmed")
            if session.outcome.is_termination_uncertain
            else translate("main", "errors.cleanupRestartRequired"),
        ) from None
