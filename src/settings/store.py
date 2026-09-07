"""Own private settings and credential changes outside ComfyUI's public storage."""

import json
import hashlib
import threading
from pathlib import Path
from ..codes import ErrorCode
from ..errors import ConnectorError
from .conflict import SettingsConflictError
from .settings import Settings, parse_settings
from ...config.settings import MAX_SETTINGS_FILE_BYTES
from ..serialization import Json, parse_json, mapping_value
from ..storage import atomic_write, read_private, private_directory
from .execution import ExecutionConfiguration, ConfigurationGeneration
from ..credentials import Credential, read_credential, save_credential, credential_source

EDITABLE_SETTINGS = frozenset(Settings().to_json())


def read_settings(directory: Path) -> Settings:
    """Read settings without creating files or directories."""
    path = directory / "settings.json"
    if not path.exists():
        return Settings()
    return parse_settings(mapping_value(parse_json(read_private(path, max_bytes=MAX_SETTINGS_FILE_BYTES).decode())))


def settings_revision(settings: Settings) -> str:
    """Identify non-secret settings so stale tabs cannot overwrite newer changes."""
    encoded = json.dumps(settings.to_json(), sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


class ConfigurationStore:
    """Serialize local changes across server and executor threads."""

    def __init__(self, directory: Path) -> None:
        """Select private storage and own the lock for settings and credential changes."""
        self.directory = directory
        self.lock = threading.Lock()
        self._generation = ConfigurationGeneration()

    def execution_snapshot(self) -> ExecutionConfiguration:
        """Read effective values together and invalidate unreadable configuration."""
        with self.lock:
            try:
                settings = read_settings(self.directory)
                credential = read_credential(self.directory)
            except ConnectorError:
                self._generation.invalidate()
                raise
            except (OSError, UnicodeError):
                self._generation.invalidate()
                raise ConnectorError(
                    ErrorCode.CONFIGURATION,
                    "Cannot load Reactor execution settings. Check the limits and private key.",
                ) from None
            return self._generation.snapshot(settings, credential)

    def status(self) -> dict[str, Json]:
        """Return presence and effective settings without returning a credential."""
        with self.lock:
            return self._status()

    def _status(self) -> dict[str, Json]:
        """Describe effective settings and key presence without returning secret values."""
        settings = read_settings(self.directory)
        source = credential_source(self.directory)
        editable = list[Json](sorted(EDITABLE_SETTINGS))
        return {
            "settings": settings.to_json(),
            "revision": settings_revision(settings),
            "credential": {"source": source, "configured": source != "missing", "verified": False},
            "editable_settings": editable,
            "catalog_available": True,
        }

    def update_settings(self, changes: dict[str, Json], revision: str) -> dict[str, Json]:
        """Apply a validated patch only to the version the editor actually read."""
        if changes.keys() - EDITABLE_SETTINGS:
            raise ConnectorError(ErrorCode.CONFIGURATION, "This setting cannot be changed here.")
        with self.lock:
            current = read_settings(self.directory)
            if revision != settings_revision(current):
                raise SettingsConflictError
            updated = parse_settings(current.to_json() | changes)
            atomic_write(
                self.directory / "settings.json",
                (json.dumps(updated.to_json(), indent=2) + "\n").encode(),
            )
            return self._status()

    def set_credential(self, value: str) -> dict[str, Json]:
        """Save a validated secret and return only the effective source."""
        credential = Credential(value)
        with self.lock:
            save_credential(self.directory, credential)
            if credential_source(self.directory) != "environment":
                self._generation.credential_saved(credential)
            return self._status()

    def clear_credential(self) -> dict[str, Json]:
        """Remove only the saved key; the server environment takes precedence."""
        with self.lock:
            path = self.directory / "credential"
            if path.is_symlink():
                raise ConnectorError(ErrorCode.CONFIGURATION, "A saved key cannot be a symbolic link.")
            if path.exists():
                private_directory(self.directory)
                path.unlink()
            if credential_source(self.directory) != "environment":
                self._generation.invalidate()
            return self._status()
