"""Errors that can be shown without exposing provider data."""

from enum import StrEnum


class ErrorCode(StrEnum):
    """Stable categories for shown error messages."""

    CONFIGURATION = "configuration"
    INTERRUPTED = "interrupted"
    INVALID_INPUT = "invalid_input"
    AUTHENTICATION = "authentication"
    UNAVAILABLE = "unavailable"
    TRANSPORT = "transport"
    TIMEOUT = "timeout"
    CAPTURE = "capture"
    CLEANUP = "cleanup"


class ConnectorError(RuntimeError):
    """An error whose message ComfyUI shows on the node."""

    def __init__(self, code: ErrorCode, message: str) -> None:
        """Store the shown message and its error category."""
        super().__init__(message)
        self.code = code
