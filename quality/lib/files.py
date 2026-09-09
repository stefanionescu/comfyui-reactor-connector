"""Repository file discovery helpers."""

from __future__ import annotations

from pathlib import Path
from .process import run_command
from ..config.repository.paths import PYTHON_SOURCE_DIRS, SHELL_SOURCE_DIRS


def read_utf8(path: Path) -> str:
    """Read one UTF-8 file or raise an error that identifies the path."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        message = f"Could not read UTF-8 file {path.as_posix()}: {error}"
        raise RuntimeError(message) from error


def git_visible_source_files(
    *,
    root: Path | None = None,
    is_existing_required: bool = False,
) -> list[str]:
    """Return tracked and untracked files below every configured source root."""
    roots = tuple(dict.fromkeys((*PYTHON_SOURCE_DIRS, *SHELL_SOURCE_DIRS)))
    return git_files(
        ["ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", *roots],
        root=root,
        is_existing_required=is_existing_required,
    )


def git_visible_files(
    *,
    root: Path | None = None,
    is_existing_required: bool = False,
) -> list[str]:
    """Return tracked and untracked non-ignored repository files."""
    return git_files(
        ["ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        root=root,
        is_existing_required=is_existing_required,
    )


def staged_files(
    *,
    root: Path | None = None,
    is_existing_required: bool = False,
) -> list[str]:
    """Return paths staged for addition, change, rename, type change, or deletion."""
    return git_files(
        ["diff", "--cached", "--no-renames", "--name-only", "--diff-filter=ACMTD", "-z"],
        root=root,
        is_existing_required=is_existing_required,
    )


def git_files(
    arguments: list[str],
    *,
    root: Path | None = None,
    is_existing_required: bool,
) -> list[str]:
    """Return null-delimited paths from a Git file-list command."""
    command = ["git", *arguments]
    try:
        result = run_command(
            command,
            is_failure_raised=True,
            is_output_captured=True,
            working_directory=root,
        )
    except RuntimeError as error:
        message = f"Git file discovery failed for {' '.join(command)}: {error}"
        raise RuntimeError(message) from error
    try:
        output = result.stdout.decode("utf-8")
    except UnicodeDecodeError as error:
        message = f"Git file discovery returned non-UTF-8 paths for {' '.join(command)}"
        raise RuntimeError(message) from error
    files = sorted({item for item in output.split("\0") if item})
    if is_existing_required:
        repository_root = root or Path.cwd()
        return [item for item in files if (repository_root / item).is_file()]
    return files
