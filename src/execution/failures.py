"""Translate SDK failures without retaining provider text in visible errors."""

from ..language import translate
from ..errors import ErrorCode, ConnectorError
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
    return ConnectorError(
        safe.code, translate("main", "errors.phase", message=str(safe), phase=phase, code=diagnostic_code(error))
    )


PROVIDER_ERRORS = {
    "UNAUTHORIZED": (ErrorCode.AUTHENTICATION, "errors.accessRefused"),
    "RATE_LIMITED": (ErrorCode.UNAVAILABLE, "errors.providerRateLimit"),
    "REQUEST_TIMEOUT": (ErrorCode.TIMEOUT, "errors.providerRequestTimeout"),
    "NOT_FOUND": (ErrorCode.UNAVAILABLE, "errors.modelUnavailable"),
    "VERSION_MISMATCH": (
        ErrorCode.UNAVAILABLE,
        "errors.modelUnavailable",
    ),
}


def safe_error(error: object) -> ConnectorError:
    """Use known error categories; never include an upstream message or URL."""
    if isinstance(error, ConnectorError):
        return error
    if isinstance(error, AuthError):
        return ConnectorError(
            ErrorCode.AUTHENTICATION,
            translate("main", "errors.authenticationFailed"),
        )
    if isinstance(error, TimeoutError):
        return ConnectorError(ErrorCode.TIMEOUT, translate("main", "errors.sessionTimeout"))
    default = (ErrorCode.TRANSPORT, "errors.runFailed")
    code, message = PROVIDER_ERRORS.get(error.code, default) if isinstance(error, ReactorError) else default
    return ConnectorError(code, translate("main", message))
