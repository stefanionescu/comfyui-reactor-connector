"""Report a settings update based on an outdated revision."""

from ..errors import ErrorCode, ConnectorError
from ..config.messages.settings import SETTINGS_CHANGED


class SettingsConflictError(ConnectorError):
    """A different request changed settings after this editor loaded them."""

    def __init__(self) -> None:
        """Tell a stale settings editor to reload before saving."""
        super().__init__(ErrorCode.CONFIGURATION, SETTINGS_CHANGED)
