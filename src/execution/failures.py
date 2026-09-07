"""Translate SDK failures without retaining provider text in visible errors."""

from ..codes import ErrorCode
from ..errors import ConnectorError
from reactor_sdk import AuthError, ReactorError


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
    return ConnectorError(safe.code, f"{safe} Stage: {phase}. Code: {diagnostic_code(error)}.")


PROVIDER_ERRORS = {
    "UNAUTHORIZED": (ErrorCode.AUTHENTICATION, "Reactor refused access. Check your key and model access."),
    "RATE_LIMITED": (ErrorCode.UNAVAILABLE, "Reactor is limiting requests. Wait before starting another run."),
    "REQUEST_TIMEOUT": (ErrorCode.TIMEOUT, "Reactor did not reply within its request limit."),
    "NOT_FOUND": (ErrorCode.UNAVAILABLE, "The requested Reactor model or protocol is unavailable. Check for updates."),
    "VERSION_MISMATCH": (
        ErrorCode.UNAVAILABLE,
        "The requested Reactor model or protocol is unavailable. Check for updates.",
    ),
}


def safe_error(error: object) -> ConnectorError:
    """Use known error categories; never include an upstream message or URL."""
    if isinstance(error, ConnectorError):
        return error
    if isinstance(error, AuthError):
        return ConnectorError(
            ErrorCode.AUTHENTICATION,
            "Reactor could not authenticate. Check your saved key and network connection.",
        )
    if isinstance(error, TimeoutError):
        return ConnectorError(ErrorCode.TIMEOUT, "Reactor exceeded the configured time limit.")
    default = (ErrorCode.TRANSPORT, "Reactor could not complete this run. Check your connection and account status.")
    code, message = PROVIDER_ERRORS.get(error.code, default) if isinstance(error, ReactorError) else default
    return ConnectorError(code, message)
