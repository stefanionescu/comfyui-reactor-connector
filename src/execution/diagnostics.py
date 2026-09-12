"""Limit saved error details and keep them in private server storage."""

import re
import json
import time
from pathlib import Path
from ..storage import atomic_write
from ..errors import ConnectorError
from reactor_sdk import ReactorError
from ..state.reports import FailureReport
from ..state.credentials import Credential
from ...config.diagnostics import MAX_CODE_CHARACTERS, MAX_MESSAGE_CHARACTERS, MAX_ERROR_NAME_CHARACTERS, REDACTIONS


def describe_failure(phase: str, error: object) -> FailureReport:
    """Limit provider error details for private diagnostics."""
    if isinstance(error, ReactorError):
        return FailureReport(phase, error.code[:MAX_CODE_CHARACTERS], error.message[:MAX_MESSAGE_CHARACTERS])
    if isinstance(error, ConnectorError) and error.diagnostic_detail:
        return FailureReport(phase, str(error.code), error.diagnostic_detail)
    return FailureReport(phase, type(error).__name__[:MAX_ERROR_NAME_CHARACTERS], str(error)[:MAX_MESSAGE_CHARACTERS])


def redact(text: str, credential: Credential) -> str:
    """Remove the known key, credential-shaped tokens, and URLs before storage."""
    text = text.replace(credential.reveal(), "[credential removed]")
    for pattern, replacement in REDACTIONS:
        text = re.sub(pattern, replacement, text)
    return text


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


__all__ = ["describe_failure", "redact", "save_failure"]
