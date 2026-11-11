"""Own private settings and credential changes outside ComfyUI's public storage."""

import json
import hashlib
from pathlib import Path
import secrets
import threading
from dataclasses import asdict, fields

from .schema import DEFAULT_SETTINGS, parse_settings
from ..errors import ErrorCode, ConnectorError
from ..storage import PRIVATE_DIRECTORY_MODE, atomic_write, read_private
from .conflict import SettingsConflictError
from ..credentials import read_credential, parse_credential, credential_source
from ..serialization import Json, parse_json, mapping_value
from ..state.settings import Settings, ExecutionConfiguration
from ..config.security import MAX_CREDENTIAL_CHARACTERS
from ..config.settings import INTEGER_SETTINGS, MAX_SETTINGS_FILE_BYTES
from ..config.messages.settings import SETTINGS_CHANGED, SETTING_READ_ONLY, SETTINGS_UNREADABLE

EDITABLE_SETTINGS = frozenset(item.name for item in fields(Settings))


class ConfigurationStore:
    """Serialize local changes across server and executor threads."""

    def __init__(self, directory: Path) -> None:
        """Select private storage and own the lock for settings and credential changes.

        Args:
            directory: The private state directory.

        """
        self.directory = directory
        # Reentrant, so a change returns the new status while it still holds the lock.
        self.lock = threading.RLock()
        # The configuration the last operation read. A removed key or an unreadable file clears it, so no later
        # operation reuses its cache token.
        self._previous: ExecutionConfiguration | None = None

    def read_execution_configuration(self) -> ExecutionConfiguration:
        """Read effective values together; renew the cache token when the settings or the key change.

        Returns:
            The settings, the key, and the cache token.

        Raises:
            ConnectorError: When the settings or the key are missing, unreadable, or not valid.

        """
        with self.lock:
            try:
                settings = read_settings(self.directory)
                credential = read_credential(self.directory)
            except ConnectorError:
                self._previous = None
                raise
            except (OSError, UnicodeError):
                self._previous = None
                raise ConnectorError(
                    ErrorCode.CONFIGURATION,
                    SETTINGS_UNREADABLE,
                ) from None
            previous = self._previous
            generation = previous.generation if previous is not None else secrets.token_hex(16)
            if previous is not None and (previous.credential != credential or previous.settings != settings):
                generation = secrets.token_hex(16)
            self._previous = ExecutionConfiguration(settings, credential, generation)
            return self._previous

    def status(self) -> dict[str, Json]:
        """Describe effective settings and key presence without returning secret values.

        Returns:
            The settings, their limits, their revision, and the source of the key.

        """
        with self.lock:
            settings, revision = read_revised_settings(self.directory)
            source = credential_source(self.directory)
            return {
                'settings': asdict(settings),
                'integer_settings': {
                    name: {'minimum': definition['minimum'], 'maximum': definition['maximum']}
                    for name, definition in INTEGER_SETTINGS.items()
                },
                'credential_limit': MAX_CREDENTIAL_CHARACTERS,
                'revision': revision,
                'credential': {'source': source},
            }

    def update_settings(self, changes: dict[str, Json], revision: str) -> dict[str, Json]:
        """Apply a validated patch only to the version the editor actually read.

        Args:
            changes: The new values, by setting name.
            revision: The revision that the editor read.

        Returns:
            The status of the store after the change.

        Raises:
            ConnectorError: When a change names a setting that is not editable.
            SettingsConflictError: When the revision is out of date.

        """
        if changes.keys() - EDITABLE_SETTINGS:
            raise ConnectorError(ErrorCode.CONFIGURATION, SETTING_READ_ONLY)
        with self.lock:
            current, current_revision = read_revised_settings(self.directory)
            if revision != current_revision:
                raise SettingsConflictError(ErrorCode.CONFIGURATION, SETTINGS_CHANGED)
            updated = parse_settings(asdict(current) | changes)
            atomic_write(
                self.directory / 'settings.json',
                (json.dumps(asdict(updated), indent=2) + '\n').encode(),
            )
            return self.status()

    def save_credential(self, value: str) -> dict[str, Json]:
        """Save a validated secret and return only the effective source.

        Args:
            value: The API key to save.

        Returns:
            The status of the store after the save.

        """
        credential = parse_credential(value)
        with self.lock:
            atomic_write(self.directory / 'credential', credential.value.encode('utf-8'))
            previous = self._previous
            # Saving the same key again keeps the cache token, so ComfyUI does not run a billed node again.
            if (
                credential_source(self.directory) != 'environment'
                and previous is not None
                and previous.credential != credential
            ):
                self._previous = None
            return self.status()

    def clear_credential(self) -> dict[str, Json]:
        """Remove only the saved key; the server environment takes precedence.

        Returns:
            The status of the store after the removal.

        """
        with self.lock:
            path = self.directory / 'credential'
            if path.exists():
                self.directory.mkdir(parents=True, exist_ok=True, mode=PRIVATE_DIRECTORY_MODE)
                path.unlink()
            if credential_source(self.directory) != 'environment':
                self._previous = None
            return self.status()


def read_settings(directory: Path) -> Settings:
    """Read settings without creating files or directories.

    Args:
        directory: The private state directory.

    Returns:
        The saved settings, or the defaults when no file exists.

    """
    path = directory / 'settings.json'
    if not path.exists():
        return DEFAULT_SETTINGS
    return parse_settings(mapping_value(parse_json(read_private(path, max_bytes=MAX_SETTINGS_FILE_BYTES).decode())))


def read_revised_settings(directory: Path) -> tuple[Settings, str]:
    """Read settings and their revision, which keeps a stale tab from overwriting newer changes.

    Args:
        directory: The private state directory.

    Returns:
        The settings and the hash that identifies their values.

    """
    settings = read_settings(directory)
    encoded = json.dumps(asdict(settings), sort_keys=True, separators=(',', ':')).encode()
    return settings, hashlib.sha256(encoded).hexdigest()
