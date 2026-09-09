"""Keep an unfinished session from being forgotten when ComfyUI restarts."""

import os
import sys
import json
import math
import stat
import time
import errno
import logging
from pathlib import Path
from functools import partial
from ...language import translate
from .state import SessionOutcome
from ...media.output import owned_io
from ...serialization import parse_json
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from ...errors import ErrorCode, ConnectorError
from ...storage import atomic_write, read_private, private_directory


class SessionReservation:
    """Hold the process lock until cleanup and keep a deadline if cleanup fails."""

    def __init__(self, directory: Path, seconds: float) -> None:
        """Prepare a single-use reservation with a finite positive lifetime."""
        if not math.isfinite(seconds) or seconds <= 0:
            msg = translate("main", "errors.sessionWaitTime")
            raise ValueError(msg)
        self.directory = directory
        self.seconds = seconds
        self._descriptor: int | None = None
        self._recorded = False
        self._used = False

    def _acquire(self) -> None:
        """Lock private session storage and record a deadline before connecting."""
        private_directory(self.directory)
        path = self.directory / "session.lock"
        if path.is_symlink():
            raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.sessionLockLink"))
        flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, flags, 0o600)
        self._descriptor = descriptor
        reservation = os.fstat(descriptor)
        if not stat.S_ISREG(reservation.st_mode) or (os.name != "nt" and reservation.st_mode & 0o077):
            raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.sessionLockPermissions"))
        _lock(descriptor)
        remaining = _remaining(self.directory / "session.json")
        if remaining > 0:
            raise ConnectorError(
                ErrorCode.CLEANUP,
                translate("main", "errors.sessionWait", seconds=math.ceil(remaining)),
            )
        atomic_write(
            self.directory / "session.json",
            json.dumps({"version": 1, "expires_at": time.time() + self.seconds}).encode(),
        )
        self._recorded = True

    def _release(self, outcome: SessionOutcome) -> None:
        """Clear only a safely ended reservation and always release the process lock."""
        try:
            if self._recorded and not outcome.is_termination_uncertain:
                atomic_write(
                    self.directory / "session.json",
                    b'{"version": 1, "expires_at": 0}',
                )
        finally:
            # Closing releases the OS lock, including when the process exits unexpectedly.
            if self._descriptor is not None:
                os.close(self._descriptor)
                self._descriptor = None

    @asynccontextmanager
    async def protect(self, outcome: SessionOutcome) -> AsyncGenerator[None, None]:
        """Write before connecting; never clear a record after an uncertain shutdown."""
        if self._used:
            msg = translate("main", "errors.reservationReused")
            raise ValueError(msg)
        self._used = True
        try:
            try:
                await owned_io(self._acquire)
            except OSError:
                raise ConnectorError(
                    ErrorCode.CONFIGURATION,
                    translate("main", "errors.sessionRecordUnreadable"),
                ) from None
            yield
        finally:
            primary_error = sys.exception()
            try:
                await owned_io(partial(self._release, outcome))
            except (OSError, ConnectorError):
                if primary_error is None:
                    raise ConnectorError(
                        ErrorCode.CONFIGURATION,
                        translate("main", "errors.sessionRecordPermissions"),
                    ) from None
                logging.getLogger(__name__).error(  # noqa: TRY400 -- reason: Tracebacks may expose private state.
                    translate("main", "errors.sessionRecordUpdateFailed")
                )


def _lock(descriptor: int) -> None:
    """Claim one local session without waiting on another ComfyUI process."""
    try:
        if sys.platform == "win32":
            import msvcrt  # noqa: PLC0415 -- reason: This lock module exists only on Windows.

            msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
        else:
            import fcntl  # noqa: PLC0415 -- reason: This lock module is unavailable on Windows.

            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as error:
        if error.errno not in {errno.EACCES, errno.EAGAIN, errno.EDEADLK}:
            raise
        raise ConnectorError(
            ErrorCode.CLEANUP,
            translate("main", "errors.sessionInOtherProcess"),
        ) from None


def _remaining(path: Path) -> float:
    """Reject damaged records instead of assuming the previous session ended."""
    try:
        raw = read_private(path, max_bytes=1024)
    except FileNotFoundError:
        return 0
    invalid = ConnectorError(
        ErrorCode.CONFIGURATION,
        translate("main", "errors.sessionRecordDamaged"),
    )
    try:
        value = parse_json(raw.decode("utf-8"), max_bytes=1024, max_depth=2)
    except (ValueError, TypeError, ConnectorError):
        raise invalid from None
    if not isinstance(value, dict) or set(value) != {"version", "expires_at"}:
        raise invalid
    if value["version"] != 1 or type(value["version"]) is not int:
        raise invalid
    expires: object = value["expires_at"]
    if type(expires) not in {int, float} or not isinstance(expires, int | float):
        raise invalid
    if not math.isfinite(expires) or expires < 0:
        raise invalid
    return max(0, expires - time.time())
