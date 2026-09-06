"""Resolve credentials without placing their values in public records."""

import os
from dataclasses import dataclass, field
from pathlib import Path

from .errors import ConnectorError, ErrorCode
from .storage import atomic_write, read_private


@dataclass(frozen=True, slots=True, repr=False)
class Credential:
    """A secret that must be revealed explicitly at the provider boundary."""

    _value: str = field(repr=False)

    def __post_init__(self) -> None:
        if not self._value or self._value != self._value.strip() or len(self._value) > 1024:
            raise ConnectorError(
                ErrorCode.CONFIGURATION, "Enter a nonempty API key without spaces."
            )
        if any(character.isspace() for character in self._value):
            raise ConnectorError(ErrorCode.CONFIGURATION, "The API key cannot contain whitespace.")

    def __repr__(self) -> str:
        return "Credential(<redacted>)"

    def __str__(self) -> str:
        return "<redacted>"

    def reveal(self) -> str:
        """Return the secret only for an authorized private provider request."""
        return self._value


def resolve_credential(directory: Path) -> Credential:
    """Prefer the server environment over private saved credentials."""
    if "REACTOR_API_KEY" in os.environ:
        return Credential(os.environ["REACTOR_API_KEY"])
    path = directory / "credential"
    if path.exists():
        try:
            return Credential(read_private(path, max_bytes=1024).decode("utf-8"))
        except (OSError, UnicodeError):
            raise ConnectorError(
                ErrorCode.CONFIGURATION,
                "Cannot read the saved Reactor key. Check its private file.",
            ) from None
    raise ConnectorError(
        ErrorCode.AUTHENTICATION,
        "Set your Reactor API key in Reactor settings or the server environment before running.",
    )


def credential_source(directory: Path) -> str:
    """Report presence and source without reading or returning the secret."""
    if "REACTOR_API_KEY" in os.environ:
        return "environment"
    return "saved" if (directory / "credential").is_file() else "missing"


def save_credential(directory: Path, credential: Credential) -> None:
    """Write a credential only to the caller's verified private state directory."""
    atomic_write(directory / "credential", credential.reveal().encode("utf-8"))
