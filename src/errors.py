"""Errors that ComfyUI can show without exposing provider data."""

from enum import StrEnum


class ErrorCode(StrEnum):
    """Stable categories for shown error messages.

    Attributes:
        CONFIGURATION: A setting, a key, or the stored state is not valid.
        INTERRUPTED: The user stopped the run.
        INVALID_INPUT: An input or a JSON value is not valid.
        AUTHENTICATION: No API key is available.
        UNAVAILABLE: The host or the browser cannot serve the request.
        TRANSPORT: The connection to the provider failed.
        TIMEOUT: The run took too long.
        CAPTURE: The recording failed.
        CLEANUP: The cleanup after a run failed.

    """

    CONFIGURATION = 'configuration'
    INTERRUPTED = 'interrupted'
    INVALID_INPUT = 'invalid_input'
    AUTHENTICATION = 'authentication'
    UNAVAILABLE = 'unavailable'
    TRANSPORT = 'transport'
    TIMEOUT = 'timeout'
    CAPTURE = 'capture'
    CLEANUP = 'cleanup'


class ConnectorError(RuntimeError):
    """An error whose message ComfyUI shows on the node."""

    def __init__(self, code: ErrorCode, message: str) -> None:
        """Store the shown message and its error category.

        Args:
            code: The category of the error.
            message: The text that ComfyUI shows.

        """
        super().__init__(message)
        self.code = code
