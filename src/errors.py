"""Errors that can be shown without exposing provider data."""

from enum import StrEnum
from ..config.diagnostics import MAX_MESSAGE_CHARACTERS


class ErrorCode(StrEnum):
    """Stable categories for UI messages and sanitized diagnostics."""

    CONFIGURATION = "configuration"
    INTERRUPTED = "interrupted"
    INVALID_INPUT = "invalid_input"
    AUTHENTICATION = "authentication"
    UNAVAILABLE = "unavailable"
    TRANSPORT = "transport"
    TIMEOUT = "timeout"
    CAPTURE = "capture"
    CLEANUP = "cleanup"
    DISCOVERY = "catalog"


class ConnectorError(RuntimeError):
    """Show reviewed text; keep optional diagnostics out of its string representation."""

    def __init__(self, code: ErrorCode, message: str, *, diagnostic_detail: str = "") -> None:
        """Store the safe message and error category separately from private diagnostic text."""
        super().__init__(message)
        self.code = code
        self.diagnostic_detail = diagnostic_detail[:MAX_MESSAGE_CHARACTERS]
