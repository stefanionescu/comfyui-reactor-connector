"""Own private settings and credential changes outside ComfyUI's public storage."""

import json
import hashlib
import threading
from pathlib import Path
from ..language import translate
from .conflict import SettingsConflictError
from .schema import Settings, parse_settings
from .execution import ExecutionConfiguration
from ..errors import ErrorCode, ConnectorError
from .execution import ConfigurationGeneration
from ...config.security import MAX_CREDENTIAL_CHARACTERS
from ..serialization import Json, parse_json, mapping_value
from ..storage import atomic_write, read_private, private_directory
from ...config.settings import INTEGER_SETTINGS, MAX_SETTINGS_FILE_BYTES
from ..credentials import Credential, read_credential, save_credential, credential_source

EDITABLE_SETTINGS = frozenset(Settings().to_json())


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
                    translate("main", "errors.settingsUnreadable"),
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
        return {
            "settings": settings.to_json(),
            "integer_settings": {
                name: {
                    "label": translate("main", "settings.limit." + name),
                    "minimum": definition["minimum"],
                    "maximum": definition["maximum"],
                }
                for name, definition in INTEGER_SETTINGS.items()
            },
            "credential_limit": MAX_CREDENTIAL_CHARACTERS,
            "revision": settings_revision(settings),
            "credential": {"source": source},
        }

    def update_settings(self, changes: dict[str, Json], revision: str) -> dict[str, Json]:
        """Apply a validated patch only to the version the editor actually read."""
        if changes.keys() - EDITABLE_SETTINGS:
            raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.settingReadOnly"))
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

    def save_credential(self, value: str) -> dict[str, Json]:
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
                raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.savedKeyLink"))
            if path.exists():
                private_directory(self.directory)
                path.unlink()
            if credential_source(self.directory) != "environment":
                self._generation.invalidate()
            return self._status()


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
