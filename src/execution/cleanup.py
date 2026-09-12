"""Finish owned cleanup despite repeated host cancellation requests."""

import sys
import asyncio
import logging
from ..language import translate
from contextlib import AsyncExitStack
from ..errors import ErrorCode, ConnectorError
from .session.resources import SessionResources


async def _release(session: SessionResources, *, failed: bool) -> None:
    """Release controls, disconnect, and reap capture even when an earlier cleanup step fails."""
    try:
        async with AsyncExitStack() as cleanup:
            cleanup.callback(session.transport.close)
            cleanup.push_async_callback(_disconnect, session)
            cleanup.push_async_callback(_release_operation, session)
            if session.track is not None:
                cleanup.callback(session.track.off_frame, session.capture.receive)
            cleanup.callback(session.events.close)
            if session.interaction is not None:
                await session.interaction.stop()
    finally:
        try:
            if session.interaction is not None:
                session.interaction.closed(
                    is_termination_confirmed=session.outcome.is_termination_confirmed,
                    failed=failed or sys.exception() is not None,
                )
        finally:
            # The capture owner terminates and reaps its child before this task completes.
            await asyncio.gather(session.worker, return_exceptions=True)


async def _release_operation(session: SessionResources) -> None:
    """Bound the time spent releasing model uploads and tracks."""
    async with asyncio.timeout(session.settings.cleanup_timeout_seconds):
        await session.operation.release(session.transport)


async def _disconnect(session: SessionResources) -> None:
    """Confirm remote termination only after disconnect finishes within its deadline."""
    async with asyncio.timeout(session.settings.cleanup_timeout_seconds):
        await session.transport.disconnect()
        session.outcome.is_termination_confirmed = True


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
