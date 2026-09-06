"""Own private settings and credential changes outside ComfyUI's public storage."""

import hashlib
import json
import threading
from pathlib import Path

from .config import Settings, parse_settings
from .credentials import Credential, credential_source, resolve_credential, save_credential
from .errors import ConnectorError, ErrorCode
from .execution_config import ConfigurationGeneration, ExecutionConfiguration
from .json_data import Json, object_value, parse_json
from .storage import atomic_write, private_directory, read_private

EDITABLE_SETTINGS = frozenset(Settings().to_json())


def load_settings(directory: Path) -> Settings:
    """Read settings without creating files or directories."""
    path = directory / "settings.json"
    if not path.exists():
        return Settings()
    return parse_settings(object_value(parse_json(read_private(path, max_bytes=65_536).decode())))


def settings_revision(settings: Settings) -> str:
    """Identify non-secret settings so stale tabs cannot overwrite newer changes."""
    encoded = json.dumps(settings.to_json(), sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


class SettingsConflict(ConnectorError):
    """A different request changed settings after this editor loaded them."""

    def __init__(self) -> None:
        super().__init__(ErrorCode.CONFIGURATION, "Settings changed. Reload them before saving.")


class ConfigurationStore:
    """Serialize local changes across server and executor threads."""

    def __init__(self, directory: Path) -> None:
        self.directory = directory
        self.lock = threading.Lock()
        self._generation = ConfigurationGeneration()

    def execution_snapshot(self) -> ExecutionConfiguration:
        """Read effective values together and invalidate unreadable configuration."""
        with self.lock:
            try:
                settings = load_settings(self.directory)
                credential = resolve_credential(self.directory)
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
        settings = load_settings(self.directory)
        source = credential_source(self.directory)
        editable: list[Json] = [key for key in sorted(EDITABLE_SETTINGS)]
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
            current = load_settings(self.directory)
            if revision != settings_revision(current):
                raise SettingsConflict()
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
                raise ConnectorError(
                    ErrorCode.CONFIGURATION, "A saved key cannot be a symbolic link."
                )
            if path.exists():
                private_directory(self.directory)
                path.unlink()
            if credential_source(self.directory) != "environment":
                self._generation.invalidate()
            return self._status()
