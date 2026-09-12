"""Resolve credentials without placing their values in public records."""

import os
from pathlib import Path
from .language import translate
from .state.credentials import Credential
from .errors import ErrorCode, ConnectorError
from .storage import atomic_write, read_private
from ..config.security import MAX_CREDENTIAL_CHARACTERS


def parse_credential(value: str) -> Credential:
    """Reject empty, oversized, or whitespace-containing API keys."""
    if not value or value != value.strip() or len(value) > MAX_CREDENTIAL_CHARACTERS:
        raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.keyEmpty"))
    if any(character.isspace() for character in value):
        raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.keyWhitespace"))
    return Credential(value)


def read_credential(directory: Path) -> Credential:
    """Prefer the server environment over private saved credentials."""
    if "REACTOR_API_KEY" in os.environ:
        return parse_credential(os.environ["REACTOR_API_KEY"])
    path = directory / "credential"
    if path.exists():
        try:
            return parse_credential(read_private(path, max_bytes=MAX_CREDENTIAL_CHARACTERS).decode("utf-8"))
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


__all__ = ["credential_source", "parse_credential", "read_credential", "save_credential"]
