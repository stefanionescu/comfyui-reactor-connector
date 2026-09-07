"""Errors that can be shown without exposing provider data."""

from .codes import ErrorCode


class ConnectorError(RuntimeError):
    """Show reviewed text; keep optional diagnostics out of its string representation."""

    def __init__(self, code: ErrorCode, message: str, *, diagnostic_detail: str = "") -> None:
        """Store the safe message and error category separately from private diagnostic text."""
        super().__init__(message)
        self.code = code
        self.diagnostic_detail = diagnostic_detail[:4096]
