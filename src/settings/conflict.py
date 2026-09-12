"""Report a settings update based on an outdated revision."""

from ..language import translate
from ..errors import ErrorCode, ConnectorError


class SettingsConflictError(ConnectorError):
    """A different request changed settings after this editor loaded them."""

    def __init__(self) -> None:
        """Tell a stale settings editor to reload before saving."""
        super().__init__(ErrorCode.CONFIGURATION, translate("main", "errors.settingsChanged"))
