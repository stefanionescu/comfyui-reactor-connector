"""Validate import placement and layout not covered by Ruff."""

from __future__ import annotations

import ast
from itertools import pairwise
from typing import TYPE_CHECKING, cast
from quality.lib.diagnostics import diagnostic

if TYPE_CHECKING:
    from collections.abc import Sequence
    from quality.lib.source import PythonSource
    from quality.lib.diagnostics import Diagnostic
    from quality.python.policy import ImportPolicy


def collect_import_layout_violations(
    source: PythonSource,
    config: ImportPolicy,
) -> list[Diagnostic]:
    """Return import placement and import-block diagnostics."""
    module = source.tree
    if module is None:
        return []
    relative_path = source.relative_path
    body = list(module.body)
    text = source.text
    lines = source.lines
    errors: list[Diagnostic] = []
    import_bodies = [body, *type_checking_bodies(body)]
    for import_body in import_bodies:
        errors.extend(import_after_statement_errors(relative_path, import_body, config))
        errors.extend(import_blank_line_errors(relative_path, lines, import_body))
        errors.extend(import_order_errors(relative_path, text, import_body))
        errors.extend(import_name_order_errors(relative_path, text, import_body))
        errors.extend(import_spacing_errors(relative_path, lines, import_body))
    return errors


def collect_import_layout_diagnostics(
    sources: Sequence[PythonSource],
    config: ImportPolicy,
) -> list[Diagnostic]:
    """Return import layout diagnostics for cached modules."""
    errors: list[Diagnostic] = []
    for source in sources:
        errors.extend(collect_import_layout_violations(source, config))
    return errors


def first_code_index(body: list[ast.stmt]) -> int:
    """Return the first non-docstring statement index."""
    if (
        body
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    ):
        return 1
    return 0


def body_imports(body: list[ast.stmt]) -> list[ast.Import | ast.ImportFrom]:
    """Return imports governed by flat length ordering."""
    imports: list[ast.Import | ast.ImportFrom] = []
    for node in body:
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            continue
        if isinstance(node, ast.Import | ast.ImportFrom):
            imports.append(node)
    return imports


def type_checking_bodies(body: list[ast.stmt]) -> list[list[ast.stmt]]:
    """Return bodies guarded by TYPE_CHECKING."""
    return [
        list(node.body)
        for node in body
        if isinstance(node, ast.If) and isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING"
    ]


def import_after_statement_errors(
    relative_path: str,
    body: list[ast.stmt],
    config: ImportPolicy,
) -> list[Diagnostic]:
    """Return imports that follow code in one governed body."""
    if relative_path in config["allow_imports_after_statements"]:
        return []
    errors: list[Diagnostic] = []
    has_seen_code = False
    for node in body[first_code_index(body) :]:
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            continue
        if isinstance(node, ast.Import | ast.ImportFrom):
            if has_seen_code:
                errors.append(
                    diagnostic(relative_path, node.lineno, "import.after-statement", "top-level import follows code"),
                )
            continue
        has_seen_code = True
    return errors


def import_blank_line_errors(
    relative_path: str,
    lines: Sequence[str],
    body: list[ast.stmt],
) -> list[Diagnostic]:
    """Return missing blank line after the import block."""
    imports = body_imports(body)
    if not imports:
        return []
    last_line = max(node.end_lineno or node.lineno for node in imports)
    if last_line < len(lines) and lines[last_line].strip():
        return [diagnostic(relative_path, last_line + 1, "import.blank-line", "blank line required after imports")]
    return []


def import_order_errors(
    relative_path: str,
    text: str,
    body: list[ast.stmt],
) -> list[Diagnostic]:
    """Require one-line imports before multiline imports using length ordering."""
    imports = body_imports(body)
    actual = [import_sort_key(node, text) for node in imports]
    if actual == sorted(actual):
        return []
    line = imports[0].lineno if imports else 1
    return [
        diagnostic(
            relative_path,
            line,
            "import.order",
            "sort one-line imports by length before grouped imports by header length",
        ),
    ]


def import_sort_key(
    node: ast.Import | ast.ImportFrom,
    text: str,
) -> tuple[int, int, str, str]:
    """Return the flat layout key for one import statement."""
    statement = import_statement_text(node, text)
    is_group = is_group_import(node, statement)
    sort_text = import_group_header(node) if is_group else statement
    return (int(is_group), *length_sort_key(sort_text))


def import_statement_text(node: ast.Import | ast.ImportFrom, text: str) -> str:
    """Return one complete import statement without surrounding indentation."""
    return cast("str", ast.get_source_segment(text, node))


def is_group_import(node: ast.Import | ast.ImportFrom, statement: str) -> bool:
    """Return whether an import is multiline or explicitly parenthesized."""
    return "\n" in statement or (isinstance(node, ast.ImportFrom) and "(" in statement)


def import_group_header(node: ast.Import | ast.ImportFrom) -> str:
    """Return the header used to order one grouped import."""
    module_name = import_module_name(node)
    return f"import {module_name}" if isinstance(node, ast.Import) else f"from {module_name} import ("


def length_sort_key(text: str) -> tuple[int, str, str]:
    """Return length-first text ordering with deterministic ties."""
    return (len(text), text.casefold(), text)


def import_module_name(node: ast.Import | ast.ImportFrom) -> str:
    """Return the full module path that owns an import statement."""
    if isinstance(node, ast.Import):
        return node.names[0].name
    prefix = "." * node.level
    return f"{prefix}{node.module or ''}"


def import_name_order_errors(
    relative_path: str,
    text: str,
    body: list[ast.stmt],
) -> list[Diagnostic]:
    """Return grouped imports whose names are not length ordered."""
    errors: list[Diagnostic] = []
    for node in body_imports(body):
        if not is_group_import(node, import_statement_text(node, text)):
            continue
        names = [imported_name_text(alias) for alias in node.names]
        actual = [length_sort_key(name) for name in names]
        if actual != sorted(actual):
            errors.append(
                diagnostic(
                    relative_path,
                    node.lineno,
                    "import.name-order",
                    "sort names inside grouped imports by length",
                ),
            )
    return errors


def imported_name_text(alias: ast.alias) -> str:
    """Return one imported name as rendered source text."""
    return f"{alias.name} as {alias.asname}" if alias.asname else alias.name


def import_spacing_errors(
    relative_path: str,
    lines: Sequence[str],
    body: list[ast.stmt],
) -> list[Diagnostic]:
    """Reject blank lines inside one flat import block."""
    imports = body_imports(body)
    errors: list[Diagnostic] = []
    for previous, current in pairwise(imports):
        previous_end = previous.end_lineno or previous.lineno
        gap = current.lineno - previous_end
        if gap != 1 or any(line.strip() for line in lines[previous_end : current.lineno - 1]):
            errors.append(diagnostic(relative_path, current.lineno, "import.spacing", "blank line inside import block"))
    return errors
