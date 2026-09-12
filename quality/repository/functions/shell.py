"""Shell function policy checks."""

from __future__ import annotations

from typing import TYPE_CHECKING
from quality.shell.parsers import collect_shell_functions, strip_shell_comments

if TYPE_CHECKING:
    from quality.lib.diagnostics import NamedDiagnostic
    from quality.repository.functions.policy import ShellFunctionPolicy


def collect_shell_function_violations(
    relative_path: str,
    source_text: str,
    policy: ShellFunctionPolicy,
) -> list[NamedDiagnostic]:
    """Return shell function policy violations."""
    errors: list[NamedDiagnostic] = []
    for function in collect_shell_functions(source_text):
        cleaned = (strip_shell_comments(str(line)).strip() for line in function["body"])
        body = [line for line in cleaned if line]
        if len(body) == 1 and ("$@" in body[0] or '"$@"' in body[0]):
            errors.append(
                {
                    "path": relative_path,
                    "line": function["start"],
                    "code": "shell.call-through",
                    "name": function["name"],
                    "message": "function only forwards arguments",
                },
            )
            continue
        if 0 < len(body) <= policy["max_trivial_statements"]:
            errors.append(
                {
                    "path": relative_path,
                    "line": function["start"],
                    "code": "shell.trivial-function",
                    "name": function["name"],
                    "message": f"function has {len(body)} nonempty code line(s)",
                },
            )
    return errors
