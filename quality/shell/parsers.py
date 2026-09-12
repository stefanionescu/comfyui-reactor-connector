"""Shell source parsers for quality checks."""

from __future__ import annotations

import re
import json
from typing import cast
from functools import lru_cache
from typing import TYPE_CHECKING, TypedDict
from quality.lib.diagnostics import diagnostic
from quality.lib.json_config import require_mapping
from quality.lib.process import run_command, ProcessContext

if TYPE_CHECKING:
    from quality.lib.diagnostics import Diagnostic


class ShellFunction(TypedDict):
    """One shell function with source extent and body lines."""

    name: str
    start: int
    end: int
    body: list[str]


FUNCTION_RE = re.compile(r"^(?P<name>[A-Za-z_][A-Za-z0-9_]*)\(\) \{$")
FUNCTION_END_RE = re.compile(r"^}$")


@lru_cache
def shell_nodes(source: str) -> tuple[dict[str, object], ...]:
    """Read shfmt's Bash syntax tree without executing the source."""
    result = run_command(
        ["shfmt", "-ln", "bash", "--to-json"],
        input_bytes=source.encode("utf-8"),
        is_output_captured=True,
        is_failure_raised=True,
        context=ProcessContext(timeout_seconds=10),
    )
    pending: list[object] = [json.loads(result.stdout)]
    nodes: list[dict[str, object]] = []
    while pending:
        value = pending.pop()
        if isinstance(value, dict):
            node = require_mapping(cast("dict[str, object]", value), "shfmt node")
            nodes.append(node)
            pending.extend(node.values())
        elif isinstance(value, list):
            pending.extend(cast("list[object]", value))
    return tuple(nodes)


def shell_literal(word: object) -> str | None:
    """Read a static shell word; expansions remain unknown instead of being guessed."""
    node = require_mapping(word, "shfmt word")
    if node.get("Type") in {"Lit", "SglQuoted"}:
        value = node.get("Value")
        return value if isinstance(value, str) else None
    parts = node.get("Parts")
    if not isinstance(parts, list):
        return None
    values = [shell_literal(part) for part in cast("list[object]", parts)]
    if any(value is None for value in values):
        return None
    return "".join(value for value in values if value is not None)


def strip_shell_comments(line: str) -> str:  # noqa: C901, PLR0912 -- reason: Keep quote, escape, and word-boundary transitions together in this line scanner.
    """Remove a line comment while preserving quoted text and hashes within words.

    This line helper does not parse nested substitutions or multiline quoting.
    Command and variable-name checks use the complete shfmt syntax tree.
    """
    quote: str | None = None
    is_escaped = False
    is_word_start = True
    for index, char in enumerate(line):
        if quote == "'":
            if char == "'":
                quote = None
            continue
        if is_escaped:
            is_escaped = False
            continue
        if char == "\\":
            is_escaped = True
            is_word_start = False
            continue
        if quote:
            if char == quote:
                quote = None
            continue
        if char == "#" and is_word_start:
            return line[:index]
        if char in {"'", '"'}:
            quote = char
        is_word_start = char.isspace() or char in ";|&()<>"
    return line


def collect_shell_functions(source: str) -> list[ShellFunction]:
    """Return shell function names, line ranges, and body lines."""
    lines = source.splitlines()
    functions: list[ShellFunction] = []
    index = 0
    while index < len(lines):
        match = FUNCTION_RE.match(lines[index])
        if not match:
            index += 1
            continue
        name = match.group("name")
        start = index + 1
        body: list[str] = []
        index += 1
        while index < len(lines):
            if FUNCTION_END_RE.match(lines[index]):
                break
            body.append(lines[index])
            index += 1
        functions.append({"name": name, "start": start, "end": index + 1, "body": body})
        index += 1
    return functions


def shell_command_references(source: str) -> dict[str, list[int]]:
    """Collect static command calls and trap callbacks; dynamic command names remain unresolved."""
    references: dict[str, list[int]] = {}
    for node in shell_nodes(source):
        if node.get("Type") != "CallExpr":
            continue
        arguments = cast("list[object]", node.get("Args", []))
        if not arguments:
            continue
        command = shell_literal(arguments[0])
        line = int(cast("int", require_mapping(node["Pos"], "command position")["Line"]))
        if command is not None:
            references.setdefault(command, []).append(line)
        if command == "trap" and len(arguments) > 1:
            callback = shell_literal(arguments[1])
            if callback:
                for name, positions in shell_command_references(callback).items():
                    references.setdefault(name, []).extend(line + offset - 1 for offset in positions)
    return references


def function_for_line(functions: list[ShellFunction], line_number: int) -> ShellFunction | None:
    """Return the function containing one source line."""
    for function in functions:
        if int(function["start"]) <= line_number <= int(function["end"]):
            return function
    return None


def check_module_length_limit(file: str, source: str, max_lines: int) -> list[Diagnostic]:
    """Return shell file-length violations."""
    line_count = len(source.splitlines())
    if line_count <= max_lines:
        return []
    return [diagnostic(file, 1, "shell.file-length", f"{line_count} lines over {max_lines}")]


def check_function_length_limit(file: str, source: str, max_lines: int) -> list[Diagnostic]:
    """Return shell function-length violations."""
    violations: list[Diagnostic] = []
    for function in collect_shell_functions(source):
        body_length = len([line for line in function["body"] if strip_shell_comments(str(line)).strip()])
        if body_length > max_lines:
            violations.append(
                diagnostic(
                    file,
                    function["start"],
                    "shell.function-length",
                    f"{function['name']} has {body_length} lines over {max_lines}",
                ),
            )
    return violations
