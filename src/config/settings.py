"""Define editable settings, their units, defaults, and supported ranges."""

from .security import MAX_SESSION_SECONDS


INTEGER_SETTINGS: dict[str, dict[str, int]] = {
    "max_session_seconds": {
        "default": 180,
        "minimum": 1,
        "maximum": MAX_SESSION_SECONDS,
    },
    "max_upload_megabytes": {"default": 100, "minimum": 1, "maximum": 4096},
}

DEFAULT_DISCOVERY_AUTO_CHECK = True

MAX_SETTINGS_BYTES = 4096

MAX_SETTINGS_FILE_BYTES = 65_536

SETTINGS_TIMEOUT_SECONDS = 5

REQUEST_CHUNK_BYTES = 1024
