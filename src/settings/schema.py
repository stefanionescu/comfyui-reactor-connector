"""Validate non-secret host limits before opening a remote session."""

from dataclasses import fields
from ..language import translate
from ..state.documents import Json
from ..state.settings import Settings
from ..errors import ErrorCode, ConnectorError
from ...config.settings import INTEGER_SETTINGS, DEFAULT_DISCOVERY_AUTO_CHECK


def default_settings() -> Settings:
    """Return the configured default for every setting."""
    return Settings(
        **{name: definition["default"] for name, definition in INTEGER_SETTINGS.items()},
        catalog_auto_check=DEFAULT_DISCOVERY_AUTO_CHECK,
    )


def validate_settings(settings: Settings) -> None:
    """Validate setting types and leave session time for setup and cleanup."""
    for item in fields(settings):
        value: object = getattr(settings, item.name)
        if item.name == "catalog_auto_check":
            valid = isinstance(value, bool)
        else:
            definition = INTEGER_SETTINGS[item.name]
            valid = type(value) is int and definition["minimum"] <= value <= definition["maximum"]
        if not valid:
            raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.settingsRange"))
    if settings.max_capture_seconds >= settings.max_session_seconds:
        raise ConnectorError(
            ErrorCode.CONFIGURATION,
            translate("main", "errors.sessionLimitTooShort"),
        )


def parse_settings(document: dict[str, Json]) -> Settings:
    """Reject unknown settings instead of silently accepting misspelled limits."""
    expected = {item.name for item in fields(Settings)}
    if document.keys() - expected:
        raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.settingUnknown"))
    defaults = default_settings()
    integers: dict[str, int] = {}
    for name in expected - {"catalog_auto_check"}:
        value = document.get(name, getattr(defaults, name))
        if type(value) is not int:
            raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.settingsWholeNumbers"))
        integers[name] = value
    automatic = document.get("catalog_auto_check", defaults.catalog_auto_check)
    if not isinstance(automatic, bool):
        raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.automaticChecksType"))
    settings = Settings(**integers, catalog_auto_check=automatic)
    validate_settings(settings)
    return settings


__all__ = ["default_settings", "parse_settings", "validate_settings"]
