"""Validate non-secret host limits before opening a remote session."""

from dataclasses import fields

from ..errors import ErrorCode, ConnectorError
from ..serialization import Json
from ..state.settings import Settings
from ..config.settings import INTEGER_SETTINGS
from ..config.messages.settings import SETTINGS_RANGE, SETTING_UNKNOWN, SETTINGS_WHOLE_NUMBERS

# Settings records cannot change, so every reader shares one record of the defaults.
DEFAULT_SETTINGS = Settings(**{name: definition['default'] for name, definition in INTEGER_SETTINGS.items()})


def validate_settings(settings: Settings) -> None:
    """Keep every limit in its range.

    Args:
        settings: The settings to check.

    Raises:
        ConnectorError: When a limit is out of its range.

    """
    for name, definition in INTEGER_SETTINGS.items():
        value: int = getattr(settings, name)
        if not definition['minimum'] <= value <= definition['maximum']:
            raise ConnectorError(ErrorCode.CONFIGURATION, SETTINGS_RANGE)


def parse_settings(document: dict[str, Json]) -> Settings:
    """Reject unknown settings instead of silently accepting misspelled limits.

    Args:
        document: The settings by name, where a missing name takes its default.

    Returns:
        The validated settings.

    Raises:
        ConnectorError: When a name is unknown or a value is not a whole number.

    """
    expected = {item.name for item in fields(Settings)}
    if document.keys() - expected:
        raise ConnectorError(ErrorCode.CONFIGURATION, SETTING_UNKNOWN)
    integers: dict[str, int] = {}
    for name in expected:
        value = document.get(name, getattr(DEFAULT_SETTINGS, name))
        if type(value) is not int:
            raise ConnectorError(ErrorCode.CONFIGURATION, SETTINGS_WHOLE_NUMBERS)
        integers[name] = value
    settings = Settings(**integers)
    validate_settings(settings)
    return settings
