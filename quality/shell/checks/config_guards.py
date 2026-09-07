"""Validate idempotent loading for shell configuration owners."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING
from quality.lib.diagnostics import diagnostic
from quality.config.shell import SHELL_CONFIG_GUARD_PATTERN

if TYPE_CHECKING:
    from quality.lib.diagnostics import Diagnostic

GUARD_RE = re.compile(SHELL_CONFIG_GUARD_PATTERN)
CONFIG_PREFIX = "scripts/config/"
GUARD_STATEMENT_COUNT = 2


def _code_lines(source: str) -> list[tuple[int, str]]:
    """Return non-empty shell lines outside comments."""
    return [
        (line_number, line.strip())
        for line_number, line in enumerate(source.splitlines(), start=1)
        if line.strip() and not line.lstrip().startswith("#")
    ]


def check_config_guards(sources: dict[str, str]) -> list[Diagnostic]:
    """Return malformed and duplicate configuration guard diagnostics."""
    errors: list[Diagnostic] = []
    owners: dict[str, str] = {}
    for path, source in sources.items():
        if not path.startswith(CONFIG_PREFIX):
            continue
        lines = _code_lines(source)
        if not lines:
            errors.append(diagnostic(path, 1, "shell.config-guard", "configuration requires an include guard"))
            continue
        line_number, statement = lines[0]
        match = GUARD_RE.fullmatch(statement)
        if match is None:
            errors.append(
                diagnostic(path, line_number, "shell.config-guard", "configuration guard must be first"),
            )
            continue
        guard_name = match.group("name")
        expected = f"readonly {guard_name}=1"
        if len(lines) < GUARD_STATEMENT_COUNT or lines[1][1] != expected:
            errors.append(diagnostic(path, line_number, "shell.config-guard", f"expected {expected}"))
        if guard_name in owners:
            errors.append(
                diagnostic(path, line_number, "shell.config-guard", f"{guard_name} is owned by {owners[guard_name]}"),
            )
        owners[guard_name] = path
    return errors
