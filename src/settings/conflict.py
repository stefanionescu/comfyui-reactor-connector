"""Report a settings update based on an outdated revision."""

from ..errors import ConnectorError


class SettingsConflictError(ConnectorError):
    """A different request changed settings after this editor loaded them."""
