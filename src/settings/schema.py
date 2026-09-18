"""Validate non-secret host limits before opening a remote session."""

from dataclasses import fields
from ..state.documents import Json
from ..state.settings import Settings
from ..errors import ErrorCode, ConnectorError
from ..config.messages.session import SESSION_LIMIT_TOO_SHORT
from ..config.settings import INTEGER_SETTINGS, DEFAULT_DISCOVERY_AUTO_CHECK
from ..config.messages.settings import SETTINGS_RANGE, SETTING_UNKNOWN, AUTOMATIC_CHECKS_TYPE, SETTINGS_WHOLE_NUMBERS


def default_settings() -> Settings:
    """Return the configured default for every setting."""
    return Settings(
        **{name: definition["default"] for name, definition in INTEGER_SETTINGS.items()},
        catalog_auto_check=DEFAULT_DISCOVERY_AUTO_CHECK,
    )


def validate_settings(settings: Settings) -> None:
    """Keep every limit in its range and leave session time for setup and cleanup."""
    for name, definition in INTEGER_SETTINGS.items():
        value: int = getattr(settings, name)
        if not definition["minimum"] <= value <= definition["maximum"]:
            raise ConnectorError(ErrorCode.CONFIGURATION, SETTINGS_RANGE)
    if settings.max_capture_seconds >= settings.max_session_seconds:
        raise ConnectorError(ErrorCode.CONFIGURATION, SESSION_LIMIT_TOO_SHORT)


def parse_settings(document: dict[str, Json]) -> Settings:
    """Reject unknown settings instead of silently accepting misspelled limits."""
    expected = {item.name for item in fields(Settings)}
    if document.keys() - expected:
        raise ConnectorError(ErrorCode.CONFIGURATION, SETTING_UNKNOWN)
    defaults = default_settings()
    integers: dict[str, int] = {}
    for name in expected - {"catalog_auto_check"}:
        value = document.get(name, getattr(defaults, name))
        if type(value) is not int:
            raise ConnectorError(ErrorCode.CONFIGURATION, SETTINGS_WHOLE_NUMBERS)
        integers[name] = value
    automatic = document.get("catalog_auto_check", defaults.catalog_auto_check)
    if not isinstance(automatic, bool):
        raise ConnectorError(ErrorCode.CONFIGURATION, AUTOMATIC_CHECKS_TYPE)
    settings = Settings(**integers, catalog_auto_check=automatic)
    validate_settings(settings)
    return settings
