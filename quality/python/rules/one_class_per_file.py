"""Enforce one top-level non-dataclass class per Python file."""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING
from quality.lib.diagnostics import diagnostic

if TYPE_CHECKING:
    from collections.abc import Sequence
    from quality.lib.source import PythonSource
    from quality.lib.diagnostics import Diagnostic


def _is_dataclass_decorator(decorator: ast.expr) -> bool:
    """Return whether a decorator marks a dataclass."""
    target: ast.expr = decorator.func if isinstance(decorator, ast.Call) else decorator
    if isinstance(target, ast.Name):
        return target.id == "dataclass"
    if isinstance(target, ast.Attribute):
        return target.attr == "dataclass"
    return False


def _base_name(base: ast.expr) -> str:
    """Return the unqualified class base name."""
    if isinstance(base, ast.Name):
        return base.id
    if isinstance(base, ast.Attribute):
        return base.attr
    return ""


def _nonconcrete_class_names(tree: ast.Module) -> set[str]:
    """Return top-level classes that define records or structural protocols."""
    nonconcrete_names: set[str] = set()
    is_changed = True
    while is_changed:
        is_changed = False
        for node in tree.body:
            if not isinstance(node, ast.ClassDef) or node.name in nonconcrete_names:
                continue
            bases = {_base_name(base) for base in node.bases}
            if bases.intersection({"Protocol", "TypedDict"}) or bases.intersection(nonconcrete_names):
                nonconcrete_names.add(node.name)
                is_changed = True
    return nonconcrete_names


def _collect_top_level_classes(source: PythonSource) -> list[str]:
    """Return non-dataclass top-level class names."""
    tree = source.tree
    if tree is None or source.path.suffix == ".pyi":
        return []

    classes: list[str] = []
    nonconcrete_names = _nonconcrete_class_names(tree)
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        if (
            any(_is_dataclass_decorator(decorator) for decorator in node.decorator_list)
            or node.name in nonconcrete_names
        ):
            continue
        classes.append(node.name)
    return classes


def collect_one_class_violations(sources: Sequence[PythonSource]) -> list[Diagnostic]:
    """Return modules with multiple concrete top-level classes."""
    violations: list[Diagnostic] = []
    for source in sources:
        classes = _collect_top_level_classes(source)
        if len(classes) > 1:
            class_names = ", ".join(classes)
            violations.append(
                diagnostic(
                    source.relative_path,
                    1,
                    "python.one-class-per-file",
                    f"{len(classes)} concrete classes: {class_names}",
                ),
            )
    return violations
