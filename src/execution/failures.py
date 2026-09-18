"""Translate SDK failures without retaining provider text in visible errors."""

from ..errors import ErrorCode, ConnectorError
from reactor_sdk import AuthError, ReactorError
from ..config.messages.discovery import MODEL_UNAVAILABLE
from ..config.messages.session import (
    PHASE,
    RUN_FAILED,
    ACCESS_REFUSED,
    SESSION_TIMEOUT,
    PROVIDER_RATE_LIMIT,
    AUTHENTICATION_FAILED,
    PROVIDER_REQUEST_TIMEOUT,
)


def diagnostic_code(error: object) -> str:
    """Return only reviewed codes; upstream messages and unknown codes remain private."""
    if isinstance(error, ReactorError):
        known = {
            "INTERNAL_ERROR",
            "NETWORK_ERROR",
            "UNAUTHORIZED",
            "NOT_FOUND",
            "CONFLICT",
            "RATE_LIMITED",
            "BAD_REQUEST",
            "SERVER_ERROR",
            "VERSION_MISMATCH",
            "DECODE_FAILED",
            "INVALID_STATE",
            "SESSION_TERMINAL",
            "MESSAGE_TOO_LARGE",
            "TRANSPORT_ERROR",
            "DISCONNECTED",
            "REQUEST_TIMEOUT",
            "ABORTED",
            "RECORDER_DISABLED",
        }
        return error.code if error.code in known else "PROVIDER_ERROR"
    for kind, code in (
        (TypeError, "TYPE_ERROR"),
        (ValueError, "VALUE_ERROR"),
        (OSError, "IO_ERROR"),
    ):
        if isinstance(error, kind):
            return code
    return "CONNECTOR_ERROR"


def phase_error(error: object, phase: str) -> ConnectorError:
    """Add a connector-owned operation name without copying a provider payload."""
    safe = safe_error(error)
    if isinstance(error, ConnectorError):
        return error
    return ConnectorError(safe.code, PHASE.format(message=str(safe), phase=phase, code=diagnostic_code(error)))


PROVIDER_ERRORS = {
    "UNAUTHORIZED": (ErrorCode.AUTHENTICATION, ACCESS_REFUSED),
    "RATE_LIMITED": (ErrorCode.UNAVAILABLE, PROVIDER_RATE_LIMIT),
    "REQUEST_TIMEOUT": (ErrorCode.TIMEOUT, PROVIDER_REQUEST_TIMEOUT),
    "NOT_FOUND": (ErrorCode.UNAVAILABLE, MODEL_UNAVAILABLE),
    "VERSION_MISMATCH": (ErrorCode.UNAVAILABLE, MODEL_UNAVAILABLE),
}


def safe_error(error: object) -> ConnectorError:
    """Use known error categories; never include an upstream message or URL."""
    if isinstance(error, ConnectorError):
        return error
    if isinstance(error, AuthError):
        return ConnectorError(
            ErrorCode.AUTHENTICATION,
            AUTHENTICATION_FAILED,
        )
    if isinstance(error, TimeoutError):
        return ConnectorError(ErrorCode.TIMEOUT, SESSION_TIMEOUT)
    default = (ErrorCode.TRANSPORT, RUN_FAILED)
    code, message = PROVIDER_ERRORS.get(error.code, default) if isinstance(error, ReactorError) else default
    return ConnectorError(code, message)
