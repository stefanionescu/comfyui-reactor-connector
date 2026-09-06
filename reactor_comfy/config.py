"""Validate non-secret host limits before opening a remote session."""

from dataclasses import asdict, dataclass, fields

from .errors import ConnectorError, ErrorCode
from .json_data import Json


@dataclass(frozen=True, slots=True)
class Settings:
    """Host limits that a workflow cannot increase."""

    max_capture_seconds: int = 60
    max_session_seconds: int = 180
    connect_timeout_seconds: int = 60
    first_frame_timeout_seconds: int = 30
    cleanup_timeout_seconds: int = 10
    queue_timeout_seconds: int = 120
    max_upload_megabytes: int = 100
    max_capture_megabytes: int = 512
    max_queue_megabytes: int = 64
    catalog_interval_hours: int = 24
    catalog_auto_check: bool = True

    def __post_init__(self) -> None:
        for item in fields(self):
            value: object = getattr(self, item.name)
            if item.name == "catalog_auto_check":
                valid = isinstance(value, bool)
            else:
                valid = type(value) is int and 1 <= value <= 3600
            if not valid:
                raise ConnectorError(
                    ErrorCode.CONFIGURATION, f"Choose a valid {item.name} setting."
                )
        if self.max_capture_seconds >= self.max_session_seconds:
            raise ConnectorError(
                ErrorCode.CONFIGURATION,
                "The session limit must exceed the capture limit to allow setup and cleanup.",
            )

    def to_json(self) -> dict[str, Json]:
        """Return only non-secret settings for the local configuration route."""
        return {key: value for key, value in asdict(self).items()}


def parse_settings(document: dict[str, Json]) -> Settings:
    """Reject unknown settings instead of silently accepting misspelled limits."""
    expected = {item.name for item in fields(Settings)}
    if document.keys() - expected:
        raise ConnectorError(ErrorCode.CONFIGURATION, "The settings contain an unknown option.")
    defaults = Settings()
    integers: dict[str, int] = {}
    for name in expected - {"catalog_auto_check"}:
        value = document.get(name, getattr(defaults, name))
        if type(value) is not int:
            raise ConnectorError(ErrorCode.CONFIGURATION, f"Use an integer for {name}.")
        integers[name] = value
    automatic = document.get("catalog_auto_check", defaults.catalog_auto_check)
    if not isinstance(automatic, bool):
        raise ConnectorError(
            ErrorCode.CONFIGURATION, "Use true or false for automatic catalog checks."
        )
    return Settings(**integers, catalog_auto_check=automatic)
