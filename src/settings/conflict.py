"""Own private settings and credential changes outside ComfyUI's public storage."""

from ..codes import ErrorCode
from ..errors import ConnectorError


class SettingsConflictError(ConnectorError):
    """A different request changed settings after this editor loaded them."""

    def __init__(self) -> None:
        """Tell a stale settings editor to reload before saving."""
        super().__init__(ErrorCode.CONFIGURATION, "Settings changed. Reload them before saving.")
