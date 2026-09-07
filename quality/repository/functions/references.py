"""Resolve repository-owned Python function references."""

from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
from collections import Counter
from typing import TYPE_CHECKING
from dataclasses import dataclass
from quality.lib.source import dotted_name

if TYPE_CHECKING:
    from collections.abc import Sequence
    from quality.lib.source import PythonSource

type Scope = tuple[str, ...]


@dataclass(frozen=True)
class ModuleFunctions:
    """Function and import identities declared by one Python module."""

    name: str
    source: PythonSource
    functions: dict[tuple[Scope, str], str]
    classes: dict[str, str]
    bindings: dict[str, str]


@dataclass(frozen=True)
class RepositoryFunctions:
    """Repository function identities and resolved reference counts."""

    modules: dict[str, ModuleFunctions]
    function_by_dotted_name: dict[str, str]
    class_by_dotted_name: dict[str, str]
    reference_counts: Counter[str]


def build_repository_functions(sources: Sequence[PythonSource]) -> RepositoryFunctions:
    """Build function identities and qualified reference counts."""
    modules = {
        module_name(source.relative_path): collect_module_functions(source)
        for source in sources
        if source.tree is not None
    }
    function_by_dotted_name: dict[str, str] = {}
    class_by_dotted_name: dict[str, str] = {}
    for record in modules.values():
        for (scope, name), identity in record.functions.items():
            function_by_dotted_name[f"{record.name}.{'.'.join((*scope, name))}"] = identity
        class_by_dotted_name.update({f"{record.name}.{name}": identity for name, identity in record.classes.items()})

    known_modules = set(modules)
    completed: dict[str, ModuleFunctions] = {}
    for module, record in modules.items():
        completed[module] = ModuleFunctions(
            name=record.name,
            source=record.source,
            functions=record.functions,
            classes=record.classes,
            bindings=import_bindings(record, known_modules),
        )

    repository = RepositoryFunctions(
        modules=completed,
        function_by_dotted_name=function_by_dotted_name,
        class_by_dotted_name=class_by_dotted_name,
        reference_counts=Counter(),
    )
    for record in completed.values():
        tree = record.source.tree
        if tree is not None:
            visitor = ReferenceVisitor(repository, record)
            visitor.visit(tree)
            repository.reference_counts.update(visitor.counts)
    return repository


def module_name(relative_path: str) -> str:
    """Return the importable module name for a repository Python path."""
    path = Path(relative_path).with_suffix("")
    parts = list(path.parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def function_identity(module: str, qualified_name: str) -> str:
    """Return the stable identity for one function definition."""
    return f"{module}:{qualified_name}"


def collect_module_functions(source: PythonSource) -> ModuleFunctions:
    """Collect functions and classes declared in one module."""
    module = module_name(source.relative_path)
    functions: dict[tuple[Scope, str], str] = {}
    classes: dict[str, str] = {}
    scope: list[str] = []

    class DefinitionVisitor(ast.NodeVisitor):
        """Collect qualified function and class definitions."""

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            """Collect one class and visit its body."""
            qualified = ".".join((*scope, node.name))
            classes[qualified] = f"{module}:{qualified}"
            scope.append(node.name)
            self.generic_visit(node)
            scope.pop()

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            """Collect one synchronous function."""
            collect_function(self, node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            """Collect one asynchronous function."""
            collect_function(self, node)

    def collect_function(
        visitor: DefinitionVisitor,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> None:
        """Collect one function and visit nested definitions."""
        key = (tuple(scope), node.name)
        qualified = ".".join((*scope, node.name))
        functions[key] = function_identity(module, qualified)
        scope.append(node.name)
        visitor.generic_visit(node)
        scope.pop()

    tree = source.tree
    if tree is not None:
        DefinitionVisitor().visit(tree)
    return ModuleFunctions(name=module, source=source, functions=functions, classes=classes, bindings={})


def import_bindings(record: ModuleFunctions, known_modules: set[str]) -> dict[str, str]:
    """Return local import names mapped to absolute identities."""
    tree = record.source.tree
    if tree is None:
        return {}
    bindings: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.Import):
            bindings.update(plain_import_bindings(node))
        elif isinstance(node, ast.ImportFrom):
            bindings.update(from_import_bindings(record, node, known_modules))
    return bindings


def plain_import_bindings(node: ast.Import) -> dict[str, str]:
    """Return bindings declared by one import statement."""
    return {
        alias.asname or alias.name.split(".", 1)[0]: alias.name if alias.asname else alias.name.split(".", 1)[0]
        for alias in node.names
    }


def from_import_bindings(
    record: ModuleFunctions,
    node: ast.ImportFrom,
    known_modules: set[str],
) -> dict[str, str]:
    """Return bindings declared by one from-import statement."""
    base = absolute_from_target(
        record.name,
        node,
        is_initializer=record.source.path.name == "__init__.py",
    )
    bindings: dict[str, str] = {}
    for alias in node.names:
        if alias.name == "*":
            continue
        identity = f"{base}.{alias.name}" if base else alias.name
        if alias.name in known_modules and not base:
            identity = alias.name
        bindings[alias.asname or alias.name] = identity
    return bindings


def absolute_from_target(module: str, node: ast.ImportFrom, *, is_initializer: bool) -> str:
    """Return the absolute target for one from-import."""
    if node.level == 0:
        return node.module or ""
    package = module if is_initializer else module.rpartition(".")[0]
    try:
        return importlib.util.resolve_name(f"{'.' * node.level}{node.module or ''}", package)
    except ImportError:
        return ""


def resolved_dotted_name(node: ast.AST, record: ModuleFunctions) -> str:
    """Return a dotted expression identity after applying import bindings."""
    name = dotted_name(node)
    if not name:
        return ""
    root, separator, tail = name.partition(".")
    bound_root = record.bindings.get(root)
    if bound_root is None and root in record.classes:
        bound_root = f"{record.name}.{root}"
    if bound_root is None:
        bound_root = root
    return f"{bound_root}.{tail}" if separator else bound_root


class ReferenceVisitor(ast.NodeVisitor):
    """Count unambiguous references to repository-owned functions."""

    def __init__(self, repository: RepositoryFunctions, record: ModuleFunctions) -> None:
        """Create a reference visitor for one module."""
        self.repository = repository
        self.record = record
        self.scope: list[str] = []
        self.class_scope: list[Scope] = []
        self.counts: Counter[str] = Counter()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit one class scope."""
        self.scope.append(node.name)
        self.class_scope.append(tuple(self.scope))
        self.generic_visit(node)
        self.class_scope.pop()
        self.scope.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit one synchronous function scope."""
        self.visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit one asynchronous function scope."""
        self.visit_function(node)

    def visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Visit one function body."""
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    def visit_Name(self, node: ast.Name) -> None:
        """Count one loaded function name."""
        if isinstance(node.ctx, ast.Load):
            identity = self.name_identity(node.id)
            if identity is not None:
                self.counts[identity] += 1

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Count one loaded class or module function attribute."""
        if isinstance(node.ctx, ast.Load):
            identity = self.attribute_identity(node)
            if identity is not None:
                self.counts[identity] += 1
        self.generic_visit(node)

    def name_identity(self, name: str) -> str | None:
        """Resolve a local or imported function name."""
        for size in range(len(self.scope), -1, -1):
            identity = self.record.functions.get((tuple(self.scope[:size]), name))
            if identity is not None:
                return identity
        imported = self.record.bindings.get(name)
        if imported is not None:
            return self.repository.function_by_dotted_name.get(imported)
        return None

    def attribute_identity(self, node: ast.Attribute) -> str | None:
        """Resolve a qualified method or module-function attribute."""
        if isinstance(node.value, ast.Name) and node.value.id in {"self", "cls"} and self.class_scope:
            class_scope = self.class_scope[-1]
            return self.record.functions.get((class_scope, node.attr))
        dotted = resolved_dotted_name(node, self.record)
        return self.repository.function_by_dotted_name.get(dotted)
