"""Resolve credentials without placing their values in public records."""

import os
from pathlib import Path
from .language import translate
from dataclasses import field, dataclass
from .errors import ErrorCode, ConnectorError
from .storage import atomic_write, read_private
from ..config.security import MAX_CREDENTIAL_CHARACTERS


@dataclass(frozen=True, slots=True, repr=False)
class Credential:
    """A secret that must be revealed explicitly at the provider boundary."""

    _value: str = field(repr=False)

    def __post_init__(self) -> None:
        """Reject empty, oversized, or whitespace-containing API keys."""
        if not self._value or self._value != self._value.strip() or len(self._value) > MAX_CREDENTIAL_CHARACTERS:
            raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.keyEmpty"))
        if any(character.isspace() for character in self._value):
            raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.keyWhitespace"))

    def __repr__(self) -> str:
        """Identify the credential type without revealing its value."""
        return "Credential(<redacted>)"

    def __str__(self) -> str:
        """Return a redacted label instead of the credential value."""
        return "<redacted>"

    def reveal(self) -> str:
        """Return the secret only for an authorized private provider request."""
        return self._value


def read_credential(directory: Path) -> Credential:
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
                translate("main", "errors.keyUnreadable"),
            ) from None
    raise ConnectorError(
        ErrorCode.AUTHENTICATION,
        translate("main", "errors.keyRequired"),
    )


def credential_source(directory: Path) -> str:
    """Report presence and source without reading or returning the secret."""
    if "REACTOR_API_KEY" in os.environ:
        return "environment"
    return "saved" if (directory / "credential").is_file() else "missing"


def save_credential(directory: Path, credential: Credential) -> None:
    """Write a credential only to the caller's verified private state directory."""
    atomic_write(directory / "credential", credential.reveal().encode("utf-8"))
