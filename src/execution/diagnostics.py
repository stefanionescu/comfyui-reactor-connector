"""Limit saved error details and keep them in private server storage."""

import re
import json
import time
from typing import Self
from pathlib import Path
from dataclasses import dataclass
from ..storage import atomic_write
from ..errors import ConnectorError
from ..credentials import Credential
from reactor_sdk import ReactorError


@dataclass(frozen=True, slots=True, repr=False)
class FailureReport:
    """Keep provider text separate from exceptions and workflow-visible results."""

    phase: str
    code: str
    message: str

    def __repr__(self) -> str:
        """Hide private failure details from object representations."""
        return "FailureDetails(<private>)"

    @classmethod
    def from_error(cls, phase: str, error: object) -> Self:
        """Limit provider error details for private diagnostics."""
        if isinstance(error, ReactorError):
            return cls(phase, error.code[:256], error.message[:4096])
        if isinstance(error, ConnectorError) and error.diagnostic_detail:
            return cls(phase, str(error.code), error.diagnostic_detail)
        return cls(phase, type(error).__name__[:128], str(error)[:4096])


def redact(text: str, credential: Credential) -> str:
    """Remove the known key, credential-shaped tokens, and URLs before storage."""
    text = text.replace(credential.reveal(), "[credential removed]")
    text = re.sub(r"(?i)\b(?:rk|sk)_[A-Za-z0-9_-]+", "[credential removed]", text)
    text = re.sub(r"\b(?:st|tk|sk)-[^\s\"'<>;,]+", "[credential removed]", text)
    text = re.sub(
        r"\b[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b",
        "[token removed]",
        text,
    )
    return re.sub(r"https?://[^\s\"'<>]+", "[URL removed]", text)


def save_failure(directory: Path, failure: FailureReport, credential: Credential, *, run_id: str | None = None) -> None:
    """Replace one private diagnostic; never add provider details to a host result."""
    document = {
        "recorded_at": time.time(),
        "phase": failure.phase,
        "code": redact(failure.code, credential),
        "message": redact(failure.message, credential),
    }
    if run_id is not None:
        document["run_id"] = run_id
    atomic_write(directory / "last-failure.json", json.dumps(document, indent=2).encode())
