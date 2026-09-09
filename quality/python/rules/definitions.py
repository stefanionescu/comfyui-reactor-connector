"""Keep module-level classes before functions."""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING
from quality.lib.diagnostics import diagnostic

if TYPE_CHECKING:
    from collections.abc import Sequence
    from quality.lib.source import PythonSource
    from quality.lib.diagnostics import Diagnostic


def collect_definition_order(sources: Sequence[PythonSource]) -> list[Diagnostic]:
    """Report classes declared after a module-level function."""
    violations: list[Diagnostic] = []
    for source in sources:
        if source.tree is None:
            continue
        has_function = False
        for node in source.tree.body:
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                has_function = True
            elif has_function and isinstance(node, ast.ClassDef):
                violations.append(
                    diagnostic(
                        source.relative_path,
                        node.lineno,
                        "python.definition-order",
                        f"Move class {node.name} before module-level functions.",
                    )
                )
    return violations
