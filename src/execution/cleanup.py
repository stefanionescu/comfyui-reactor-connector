"""Finish owned cleanup despite repeated host cancellation requests."""

import sys
from typing import TYPE_CHECKING, cast
import asyncio
import logging
from contextlib import AsyncExitStack

from ..tasks import wait_shielded
from ..errors import ErrorCode, ConnectorError
from .x2.operation import X2Operation
from .sana.operation import SanaOperation
from .lingbot.operation import LingBotOperation
from .session.resources import SessionResources
from ..config.messages.session import (
    CLEANUP_UNCONFIRMED,
    LOCAL_CLEANUP_FAILED,
    TERMINATION_UNCONFIRMED,
    CLEANUP_RESTART_REQUIRED,
)
from ..config.generation.session import CLEANUP_TIMEOUT_SECONDS

if TYPE_CHECKING:
    from .transport import FrameRegistration


async def _release(session: SessionResources, *, failed: bool) -> None:
    """Release controls, disconnect, and reap capture even when an earlier cleanup step fails.

    Args:
        session: The resources of the session to release.
        failed: Whether the session ended with an error.

    """
    try:
        async with AsyncExitStack() as cleanup:
            cleanup.callback(session.transport.close)
            cleanup.push_async_callback(_end_remote_session, session)
            if session.track is not None:
                cleanup.callback(cast('FrameRegistration', session.track.off_frame), session.capture.receive)
            cleanup.callback(session.events.close)
            if session.interaction is not None:
                await session.interaction.stop()
    finally:
        try:
            if session.interaction is not None:
                session.interaction.closed(
                    session.outcome.is_termination_confirmed,
                    failed or sys.exception() is not None,
                )
        finally:
            # The capture owner terminates and reaps its child before this task completes.
            await asyncio.gather(session.worker, return_exceptions=True)


async def _end_remote_session(session: SessionResources) -> None:
    """Release model uploads and tracks, then disconnect even when the release fails.

    Each step has its own deadline. Remote termination counts as confirmed only after disconnect finishes in time.

    Args:
        session: The session whose model controls and connection end.

    """
    try:
        async with asyncio.timeout(CLEANUP_TIMEOUT_SECONDS):
            # Only these models hold controls, uploads, or source tracks that need a release before disconnect.
            if isinstance(session.operation, (LingBotOperation, SanaOperation, X2Operation)):
                await session.operation.release(session.transport)
    finally:
        async with asyncio.timeout(CLEANUP_TIMEOUT_SECONDS):
            if session.transport.client is not None:
                await session.transport.client.disconnect()
            session.outcome.is_termination_confirmed = True


async def finish_session(session: SessionResources, primary_error: BaseException | None) -> None:
    """Preserve the original failure and await one cleanup task exactly once.

    Args:
        session: The session to stop and clean up.
        primary_error: The failure that ended the session, or None after success.

    Raises:
        ConnectorError: When cleanup fails and no earlier failure exists.
        asyncio.CancelledError: When the host cancelled the wait for cleanup.

    """
    session.capture.stop()
    cleanup = asyncio.create_task(_release(session, failed=primary_error is not None))
    cancelled = await wait_shielded(cleanup)
    error = cleanup.exception()
    # A connection attempt without a confirmed termination may still bill.
    is_termination_uncertain = session.outcome.is_connection_attempted and not session.outcome.is_termination_confirmed
    if error is not None:
        message = CLEANUP_UNCONFIRMED if is_termination_uncertain else LOCAL_CLEANUP_FAILED
        logging.getLogger(__name__).error(message)
    if cancelled:
        raise asyncio.CancelledError
    if error is not None and primary_error is None:
        raise ConnectorError(
            ErrorCode.CLEANUP,
            TERMINATION_UNCONFIRMED if is_termination_uncertain else CLEANUP_RESTART_REQUIRED,
        ) from None
