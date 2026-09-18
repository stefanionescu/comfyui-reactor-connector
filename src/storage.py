"""Private, atomic storage outside the installed package."""

import os
import sys
import tempfile
from pathlib import Path
from .errors import ErrorCode, ConnectorError
from .config.messages.settings import STATE_FILE_SIZE, STATE_DIRECTORY_ABSOLUTE


def state_directory() -> Path:
    """Choose the platform's private connector state location without creating it."""
    override = os.environ.get("REACTOR_COMFY_STATE_DIRECTORY")
    if override:
        path = Path(override).expanduser()
        if not path.is_absolute():
            raise ConnectorError(ErrorCode.CONFIGURATION, STATE_DIRECTORY_ABSOLUTE)
        return path
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "ReactorComfyUI"
    if sys.platform == "win32":
        return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "ReactorComfyUI"
    return Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state")) / "reactor-comfy"


def private_directory(directory: Path) -> None:
    """Create the owner-only state directory."""
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)


def atomic_write(path: Path, content: bytes) -> None:
    """Replace one state file only after its complete private write succeeds."""
    private_directory(path.parent)
    descriptor, temporary = tempfile.mkstemp(prefix=".reactor-", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        # reason: Callers use fixed state filenames; both paths are in the owner-configured private directory.
        # bearer:disable python_lang_path_traversal
        temporary_path.replace(path)
    finally:
        temporary_path.unlink(missing_ok=True)


def read_private(path: Path, *, max_bytes: int) -> bytes:
    """Read a state file within its size limit."""
    with path.open("rb") as stream:
        content = stream.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise ConnectorError(ErrorCode.CONFIGURATION, STATE_FILE_SIZE)
    return content
