"""Define editable settings, their units, defaults, and supported ranges."""

from .security import MAX_SESSION_SECONDS


INTEGER_SETTINGS: dict[str, dict[str, int]] = {
    "max_capture_seconds": {
        "default": 60,
        "minimum": 1,
        "maximum": MAX_SESSION_SECONDS,
    },
    "max_session_seconds": {
        "default": 180,
        "minimum": 1,
        "maximum": MAX_SESSION_SECONDS,
    },
    "connect_timeout_seconds": {
        "default": 60,
        "minimum": 1,
        "maximum": MAX_SESSION_SECONDS,
    },
    "first_frame_timeout_seconds": {
        "default": 30,
        "minimum": 1,
        "maximum": MAX_SESSION_SECONDS,
    },
    "cleanup_timeout_seconds": {
        "default": 10,
        "minimum": 1,
        "maximum": MAX_SESSION_SECONDS,
    },
    "queue_timeout_seconds": {
        "default": 120,
        "minimum": 1,
        "maximum": MAX_SESSION_SECONDS,
    },
    "max_upload_megabytes": {"default": 100, "minimum": 1, "maximum": 4096},
    "max_capture_megabytes": {"default": 512, "minimum": 1, "maximum": 4096},
    "max_queue_megabytes": {"default": 64, "minimum": 1, "maximum": 4096},
    "catalog_interval_hours": {"default": 24, "minimum": 1, "maximum": 8760},
}

DEFAULT_DISCOVERY_AUTO_CHECK = True

MAX_SETTINGS_BYTES = 4096

MAX_SETTINGS_FILE_BYTES = 65_536

SETTINGS_TIMEOUT_SECONDS = 5

REQUEST_CHUNK_BYTES = 1024

__all__ = [
    "DEFAULT_DISCOVERY_AUTO_CHECK",
    "INTEGER_SETTINGS",
    "MAX_SETTINGS_BYTES",
    "MAX_SETTINGS_FILE_BYTES",
    "REQUEST_CHUNK_BYTES",
    "SETTINGS_TIMEOUT_SECONDS",
]
