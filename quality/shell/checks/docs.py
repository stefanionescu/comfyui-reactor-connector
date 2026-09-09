"""Validate shell function documentation."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING
from quality.lib.diagnostics import diagnostic
from quality.config.shell import SHELL_RUNTIME_HEADER
from quality.shell.parsers import collect_shell_functions
from quality.shell.checks.bash import is_architecture_source

if TYPE_CHECKING:
    from pathlib import Path
    from quality.lib.diagnostics import Diagnostic
    from quality.shell.parsers import ShellFunction

SUMMARY_RE = re.compile(r"^# (?P<name>[A-Za-z_][A-Za-z0-9_]*) - (?P<summary>.+)$")
SUMMARY_WORD_RE = re.compile(r"[A-Za-z0-9]+")
VAGUE_SUMMARY_WORDS = {
    "a",
    "an",
    "and",
    "execute",
    "executes",
    "handle",
    "handles",
    "perform",
    "performs",
    "run",
    "runs",
    "the",
}


def function_doc_block(lines: list[str], declaration_line: int) -> list[str]:
    """Return the contiguous comment block before one function."""
    index = declaration_line - 2
    block: list[str] = []
    while index >= 0 and lines[index].startswith("#"):
        block.append(lines[index].rstrip())
        index -= 1
    block.reverse()
    return block


def has_meaningful_summary(name: str, summary: str) -> bool:
    """Return whether a summary adds information beyond the function name."""
    name_words = set(name.removeprefix("_").split("_"))
    summary_words = {
        word.lower() for word in SUMMARY_WORD_RE.findall(summary) if word.lower() not in VAGUE_SUMMARY_WORDS
    }
    return bool(summary_words - name_words)


def check_function_doc(
    path: str,
    function: ShellFunction,
    lines: list[str],
) -> list[Diagnostic]:
    """Return documentation diagnostics for one shell function."""
    name = str(function["name"])
    start = int(function["start"])
    block = function_doc_block(lines, start)
    if not block:
        return [diagnostic(path, start, "shell.function-doc", f"{name} requires a function comment")]
    summary_match = SUMMARY_RE.fullmatch(block[0])
    if summary_match is None or summary_match.group("name") != name:
        return [
            diagnostic(
                path,
                start,
                "shell.function-doc",
                f"{name} requires an immediate '# {name} - ...' summary",
            ),
        ]
    errors: list[Diagnostic] = []
    summary = summary_match.group("summary")
    if not has_meaningful_summary(name, summary):
        errors.append(
            diagnostic(
                path,
                start,
                "shell.function-summary",
                f"{name} summary must describe concrete behavior",
            ),
        )
    return errors


def check_shell_docs(sources: dict[str, str], _root: Path) -> list[Diagnostic]:
    """Return diagnostics for undocumented shell functions."""
    errors: list[Diagnostic] = []
    for path, source in sources.items():
        if not is_architecture_source(path):
            continue
        lines = source.splitlines()
        if SHELL_RUNTIME_HEADER not in lines[:4]:
            errors.append(diagnostic(path, 1, "shell.runtime-header", f"Add {SHELL_RUNTIME_HEADER}"))
        for function in collect_shell_functions(source):
            errors.extend(check_function_doc(path, function, lines))
    return errors
