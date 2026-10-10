"""Translate SDK failures into shown errors that include Reactor's own message."""

import re
from ..errors import ErrorCode, ConnectorError
from reactor_sdk import AuthError, ReactorError
from ..config.diagnostics import REDACTIONS, MAX_MESSAGE_CHARACTERS
from ..config.messages.session import (
    PHASE,
    RUN_FAILED,
    ACCESS_REFUSED,
    SESSION_TIMEOUT,
    PROVIDER_MESSAGE,
    MODEL_UNAVAILABLE,
    PROVIDER_RATE_LIMIT,
    AUTHENTICATION_FAILED,
    PROVIDER_REQUEST_TIMEOUT,
)


def provider_text(text: str) -> str:
    """Remove keys, tokens, and URLs from Reactor's text and keep it short."""
    for pattern, replacement in REDACTIONS:
        text = re.sub(pattern, replacement, text)
    return text.strip()[:MAX_MESSAGE_CHARACTERS]


def error_code(error: object) -> str:
    """Return Reactor's own code, or a code naming the local failure."""
    if isinstance(error, ReactorError):
        return error.code
    for kind, code in (
        (TypeError, "TYPE_ERROR"),
        (ValueError, "VALUE_ERROR"),
        (OSError, "IO_ERROR"),
    ):
        if isinstance(error, kind):
            return code
    return "CONNECTOR_ERROR"


def phase_error(error: object, phase: str) -> ConnectorError:
    """Name the failed operation and add Reactor's own message when it sent one."""
    if isinstance(error, ConnectorError):
        return error
    safe = safe_error(error)
    message = PHASE.format(message=str(safe), phase=phase, code=error_code(error))
    detail = provider_text(error.message) if isinstance(error, ReactorError) else ""
    if detail:
        message = f"{message} {PROVIDER_MESSAGE.format(message=detail)}"
    return ConnectorError(safe.code, message)


PROVIDER_ERRORS = {
    "UNAUTHORIZED": (ErrorCode.AUTHENTICATION, ACCESS_REFUSED),
    "RATE_LIMITED": (ErrorCode.UNAVAILABLE, PROVIDER_RATE_LIMIT),
    "REQUEST_TIMEOUT": (ErrorCode.TIMEOUT, PROVIDER_REQUEST_TIMEOUT),
    "NOT_FOUND": (ErrorCode.UNAVAILABLE, MODEL_UNAVAILABLE),
    "VERSION_MISMATCH": (ErrorCode.UNAVAILABLE, MODEL_UNAVAILABLE),
}


def safe_error(error: object) -> ConnectorError:
    """Map an SDK failure to a connector error category and its message."""
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
