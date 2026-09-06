"""Translate SDK failures without retaining provider text in visible errors."""

from reactor_sdk import AuthError, ReactorError

from ..errors import ConnectorError, ErrorCode


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
    if isinstance(error, ReactorError):
        match error.code:
            case "UNAUTHORIZED":
                return ConnectorError(
                    ErrorCode.AUTHENTICATION,
                    "Reactor refused access. Check your key and model access.",
                )
            case "RATE_LIMITED":
                return ConnectorError(
                    ErrorCode.UNAVAILABLE,
                    "Reactor is limiting requests. Wait before starting another run.",
                )
            case "REQUEST_TIMEOUT":
                return ConnectorError(
                    ErrorCode.TIMEOUT, "Reactor did not reply within its request limit."
                )
            case "NOT_FOUND" | "VERSION_MISMATCH":
                return ConnectorError(
                    ErrorCode.UNAVAILABLE,
                    "The requested Reactor model or protocol is unavailable. Check for updates.",
                )
            case _:
                pass
    return ConnectorError(
        ErrorCode.TRANSPORT,
        "Reactor could not complete this run. Check your connection and account status.",
    )
