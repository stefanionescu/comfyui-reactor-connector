"""Private, atomic storage outside the installed package."""

import os
import sys
import stat
import tempfile
from pathlib import Path
from .language import translate
from .errors import ErrorCode, ConnectorError


def state_directory() -> Path:
    """Choose the platform's private connector state location without creating it."""
    override = os.environ.get("REACTOR_COMFY_STATE_DIRECTORY")
    if override:
        path = Path(override).expanduser()
        if not path.is_absolute():
            raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.stateDirectoryAbsolute"))
        return path
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "ReactorComfyUI"
    if sys.platform == "win32":
        return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "ReactorComfyUI"
    return Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state")) / "reactor-comfy"


def private_directory(directory: Path) -> None:
    """Create a private directory, rejecting a symlink at its final component."""
    if directory.is_symlink():
        raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.stateDirectoryLink"))
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    if os.name != "nt" and directory.stat().st_mode & 0o077:
        raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.stateDirectoryPermissions"))


def atomic_write(path: Path, content: bytes) -> None:
    """Replace one state file only after its complete private write succeeds."""
    private_directory(path.parent)
    if path.is_symlink():
        raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.stateFileLink"))
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
    """Limit bytes read and reject a file whose path ends in a symbolic link."""
    before = path.stat(follow_symlinks=False)
    if not stat.S_ISREG(before.st_mode):
        raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.stateFileType"))
    if os.name != "nt" and before.st_mode & 0o077:
        raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.stateFilePermissions"))
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    with os.fdopen(os.open(path, flags), "rb") as stream:
        after = os.fstat(stream.fileno())
        if (
            not stat.S_ISREG(after.st_mode)
            or (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino)
            or (os.name != "nt" and after.st_mode & 0o077)
        ):
            raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.stateFileChanged"))
        content = stream.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.stateFileSize"))
    return content
