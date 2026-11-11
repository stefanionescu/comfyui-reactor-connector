"""Resolve credentials without placing their values in public records."""

import os
from pathlib import Path

from .errors import ErrorCode, ConnectorError
from .storage import read_private
from .config.security import MAX_CREDENTIAL_CHARACTERS
from .state.credentials import Credential
from .config.messages.settings import KEY_EMPTY, KEY_REQUIRED, KEY_UNREADABLE, KEY_WHITESPACE


def parse_credential(value: str) -> Credential:
    """Reject empty, oversized, or whitespace-containing API keys.

    Args:
        value: The API key to check.

    Returns:
        The credential that holds the key.

    Raises:
        ConnectorError: When the key is empty, too long, or contains whitespace.

    """
    if not value or value != value.strip() or len(value) > MAX_CREDENTIAL_CHARACTERS:
        raise ConnectorError(ErrorCode.CONFIGURATION, KEY_EMPTY.format(maximum=MAX_CREDENTIAL_CHARACTERS))
    if any(character.isspace() for character in value):
        raise ConnectorError(ErrorCode.CONFIGURATION, KEY_WHITESPACE)
    return Credential(value)


def read_credential(directory: Path) -> Credential:
    """Prefer the server environment over private saved credentials.

    Args:
        directory: The private state directory that holds the saved key.

    Returns:
        The credential from the environment or from the saved file.

    Raises:
        ConnectorError: When no key is set, or the saved key is unreadable or not valid.

    """
    if 'REACTOR_API_KEY' in os.environ:
        return parse_credential(os.environ['REACTOR_API_KEY'])
    path = directory / 'credential'
    if path.exists():
        try:
            return parse_credential(read_private(path, max_bytes=MAX_CREDENTIAL_CHARACTERS).decode('utf-8'))
        except (OSError, UnicodeError):
            raise ConnectorError(
                ErrorCode.CONFIGURATION,
                KEY_UNREADABLE,
            ) from None
    raise ConnectorError(
        ErrorCode.AUTHENTICATION,
        KEY_REQUIRED,
    )


def credential_source(directory: Path) -> str:
    """Report presence and source without reading or returning the secret.

    Args:
        directory: The private state directory that holds the saved key.

    Returns:
        The source of the key, or a word that says the key is missing.

    """
    if 'REACTOR_API_KEY' in os.environ:
        return 'environment'
    return 'saved' if (directory / 'credential').is_file() else 'missing'
