"""Check the Bash syntax contract used by local tasks, hooks, and quality tools."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING
from quality.lib.diagnostics import diagnostic
from quality.shell.parsers import strip_shell_comments
from quality.config.shell import BASH_SHEBANGS, SHELL_BASH_4_PATTERNS, SHELL_ARCHITECTURE_PREFIXES

if TYPE_CHECKING:
    from pathlib import Path
    from quality.lib.diagnostics import Diagnostic

DIRECTORY_ASSIGNMENT_RE = re.compile(
    r"^(?P<name>[A-Z_][A-Z0-9_]*)=.*\bcd\b.*BASH_SOURCE\[0\].*\bpwd(?: -P)?\)",
)


def is_architecture_source(path: str) -> bool:
    """Return whether a shell path uses repository script architecture."""
    matches = path.startswith(SHELL_ARCHITECTURE_PREFIXES)
    if not matches:
        return False
    return path.endswith(".sh") or path.startswith((".mise/tasks/", ".githooks/"))


def is_file_executable(path: Path) -> bool:
    """Return whether a file has any executable mode bit."""
    mode = path.stat().st_mode
    executable_bits = mode & 0o111
    return executable_bits != 0


def check_directory_constants(path: str, source: str) -> list[Diagnostic]:
    """Return diagnostics for unsafe computed directory constants."""
    lines = source.splitlines()
    errors: list[Diagnostic] = []
    for line_number, line in enumerate(lines, start=1):
        code = strip_shell_comments(line).strip()
        match = DIRECTORY_ASSIGNMENT_RE.match(code)
        if match is None:
            continue
        if "CDPATH=" not in code or "cd --" not in code or "pwd -P" not in code or "||" not in code:
            errors.append(
                diagnostic(
                    path,
                    line_number,
                    "shell.directory-resolution",
                    "computed directories require CDPATH, cd --, pwd -P, and an explicit failure path",
                ),
            )
    return errors


def check_bash_compatibility(path: str, source: str) -> list[Diagnostic]:
    """Return diagnostics for syntax newer than the declared project runtime."""
    errors: list[Diagnostic] = []
    for pattern, message in SHELL_BASH_4_PATTERNS:
        compiled = re.compile(pattern)
        for line_number, line in enumerate(source.splitlines(), start=1):
            code = strip_shell_comments(line)
            if compiled.search(code):
                errors.append(diagnostic(path, line_number, "shell.bash-version", message))
    return errors


def check_bash_scripts(sources: dict[str, str], _root: Path) -> list[Diagnostic]:
    """Check interpreter declarations, computed paths, and supported Bash syntax."""
    errors: list[Diagnostic] = []
    for path, source in sources.items():
        lines = source.splitlines()
        if lines and lines[0] not in BASH_SHEBANGS:
            errors.append(diagnostic(path, 1, "shell.shebang", "shell scripts must use Bash"))
        errors.extend(check_directory_constants(path, source))
        errors.extend(check_bash_compatibility(path, source))
    return errors
