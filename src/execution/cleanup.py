"""Finish owned cleanup despite repeated host cancellation requests."""

import sys
import asyncio
import logging
from ..tasks import wait_shielded
from contextlib import AsyncExitStack
from ..errors import ErrorCode, ConnectorError
from .session.resources import SessionResources
from ..config.generation.session import CLEANUP_TIMEOUT_SECONDS
from ..config.messages.session import (
    CLEANUP_UNCONFIRMED,
    LOCAL_CLEANUP_FAILED,
    TERMINATION_UNCONFIRMED,
    CLEANUP_RESTART_REQUIRED,
)


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
    async with asyncio.timeout(CLEANUP_TIMEOUT_SECONDS):
        await session.operation.release(session.transport)


async def _disconnect(session: SessionResources) -> None:
    """Confirm remote termination only after disconnect finishes within its deadline."""
    async with asyncio.timeout(CLEANUP_TIMEOUT_SECONDS):
        await session.transport.disconnect()
        session.outcome.is_termination_confirmed = True


async def finish_session(session: SessionResources, primary_error: BaseException | None) -> None:
    """Preserve the original failure and await one cleanup task exactly once."""
    session.capture.stop()
    cleanup = asyncio.create_task(_release(session, failed=primary_error is not None))
    cancelled = await wait_shielded(cleanup)
    error = cleanup.exception()
    if error is not None:
        message = CLEANUP_UNCONFIRMED if session.outcome.is_termination_uncertain else LOCAL_CLEANUP_FAILED
        logging.getLogger(__name__).error(message)
    if cancelled:
        raise asyncio.CancelledError
    if error is not None and primary_error is None:
        raise ConnectorError(
            ErrorCode.CLEANUP,
            TERMINATION_UNCONFIRMED if session.outcome.is_termination_uncertain else CLEANUP_RESTART_REQUIRED,
        ) from None
