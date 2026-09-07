"""Errors that can be shown without exposing provider data."""

from enum import StrEnum


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
    BUDGET = "budget"
    DISCOVERY = "catalog"
