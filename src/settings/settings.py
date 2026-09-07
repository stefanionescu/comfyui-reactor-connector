"""Validate non-secret host limits before opening a remote session."""

from ..codes import ErrorCode
from ..serialization import Json
from ..errors import ConnectorError
from dataclasses import asdict, fields, dataclass
from ...config.settings import (
    MAX_TIMEOUT_SECONDS,
    DEFAULT_MAX_CAPTURE_SECONDS,
    DEFAULT_MAX_QUEUE_MEGABYTES,
    DEFAULT_MAX_SESSION_SECONDS,
    DEFAULT_DISCOVERY_AUTO_CHECK,
    DEFAULT_MAX_UPLOAD_MEGABYTES,
    DEFAULT_FRAME_TIMEOUT_SECONDS,
    DEFAULT_MAX_CAPTURE_MEGABYTES,
    DEFAULT_QUEUE_TIMEOUT_SECONDS,
    DEFAULT_CLEANUP_TIMEOUT_SECONDS,
    DEFAULT_CONNECT_TIMEOUT_SECONDS,
    DEFAULT_DISCOVERY_INTERVAL_HOURS,
)


@dataclass(frozen=True, slots=True)
class Settings:
    """Host limits that a workflow cannot increase."""

    max_capture_seconds: int = DEFAULT_MAX_CAPTURE_SECONDS
    max_session_seconds: int = DEFAULT_MAX_SESSION_SECONDS
    connect_timeout_seconds: int = DEFAULT_CONNECT_TIMEOUT_SECONDS
    first_frame_timeout_seconds: int = DEFAULT_FRAME_TIMEOUT_SECONDS
    cleanup_timeout_seconds: int = DEFAULT_CLEANUP_TIMEOUT_SECONDS
    queue_timeout_seconds: int = DEFAULT_QUEUE_TIMEOUT_SECONDS
    max_upload_megabytes: int = DEFAULT_MAX_UPLOAD_MEGABYTES
    max_capture_megabytes: int = DEFAULT_MAX_CAPTURE_MEGABYTES
    max_queue_megabytes: int = DEFAULT_MAX_QUEUE_MEGABYTES
    catalog_interval_hours: int = DEFAULT_DISCOVERY_INTERVAL_HOURS
    catalog_auto_check: bool = DEFAULT_DISCOVERY_AUTO_CHECK

    def __post_init__(self) -> None:
        """Validate setting types and leave session time for setup and cleanup."""
        for item in fields(self):
            value: object = getattr(self, item.name)
            if item.name == "catalog_auto_check":
                valid = isinstance(value, bool)
            else:
                valid = type(value) is int and 1 <= value <= MAX_TIMEOUT_SECONDS
            if not valid:
                raise ConnectorError(ErrorCode.CONFIGURATION, f"Choose a valid {item.name} setting.")
        if self.max_capture_seconds >= self.max_session_seconds:
            raise ConnectorError(
                ErrorCode.CONFIGURATION,
                "The session limit must exceed the capture limit to allow setup and cleanup.",
            )

    def to_json(self) -> dict[str, Json]:
        """Return only non-secret settings for the local configuration route."""
        return dict(asdict(self).items())


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
        raise ConnectorError(ErrorCode.CONFIGURATION, "Use true or false for automatic catalog checks.")
    return Settings(**integers, catalog_auto_check=automatic)
