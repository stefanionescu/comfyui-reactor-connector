"""Validate non-secret host limits before opening a remote session."""

from ..language import translate
from ..serialization import Json
from ..errors import ErrorCode, ConnectorError
from dataclasses import asdict, fields, dataclass
from ...config.settings import INTEGER_SETTINGS, DEFAULT_DISCOVERY_AUTO_CHECK


@dataclass(frozen=True, slots=True)
class Settings:
    """Host limits that a workflow cannot increase."""

    max_capture_seconds: int = INTEGER_SETTINGS["max_capture_seconds"]["default"]
    max_session_seconds: int = INTEGER_SETTINGS["max_session_seconds"]["default"]
    connect_timeout_seconds: int = INTEGER_SETTINGS["connect_timeout_seconds"]["default"]
    first_frame_timeout_seconds: int = INTEGER_SETTINGS["first_frame_timeout_seconds"]["default"]
    cleanup_timeout_seconds: int = INTEGER_SETTINGS["cleanup_timeout_seconds"]["default"]
    queue_timeout_seconds: int = INTEGER_SETTINGS["queue_timeout_seconds"]["default"]
    max_upload_megabytes: int = INTEGER_SETTINGS["max_upload_megabytes"]["default"]
    max_capture_megabytes: int = INTEGER_SETTINGS["max_capture_megabytes"]["default"]
    max_queue_megabytes: int = INTEGER_SETTINGS["max_queue_megabytes"]["default"]
    catalog_interval_hours: int = INTEGER_SETTINGS["catalog_interval_hours"]["default"]
    catalog_auto_check: bool = DEFAULT_DISCOVERY_AUTO_CHECK

    def __post_init__(self) -> None:
        """Validate setting types and leave session time for setup and cleanup."""
        for item in fields(self):
            value: object = getattr(self, item.name)
            if item.name == "catalog_auto_check":
                valid = isinstance(value, bool)
            else:
                definition = INTEGER_SETTINGS[item.name]
                valid = type(value) is int and definition["minimum"] <= value <= definition["maximum"]
            if not valid:
                raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.settingsRange"))
        if self.max_capture_seconds >= self.max_session_seconds:
            raise ConnectorError(
                ErrorCode.CONFIGURATION,
                translate("main", "errors.sessionLimitTooShort"),
            )

    def to_json(self) -> dict[str, Json]:
        """Return only non-secret settings for the local configuration route."""
        return dict(asdict(self).items())


def parse_settings(document: dict[str, Json]) -> Settings:
    """Reject unknown settings instead of silently accepting misspelled limits."""
    expected = {item.name for item in fields(Settings)}
    if document.keys() - expected:
        raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.settingUnknown"))
    defaults = Settings()
    integers: dict[str, int] = {}
    for name in expected - {"catalog_auto_check"}:
        value = document.get(name, getattr(defaults, name))
        if type(value) is not int:
            raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.settingsWholeNumbers"))
        integers[name] = value
    automatic = document.get("catalog_auto_check", defaults.catalog_auto_check)
    if not isinstance(automatic, bool):
        raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.automaticChecksType"))
    return Settings(**integers, catalog_auto_check=automatic)
