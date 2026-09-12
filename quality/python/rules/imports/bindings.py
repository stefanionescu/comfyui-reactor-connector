"""Resolve import aliases within lexical scopes, without executing Python source."""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

COMPREHENSION_TYPES = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)

SCOPE_TYPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)


def local_nodes(statements: Sequence[ast.AST]) -> Iterator[ast.AST]:
    """Walk one lexical body without collecting declarations from nested scopes."""
    for node in statements:
        yield node
        if not isinstance(node, (*SCOPE_TYPES, *COMPREHENSION_TYPES)):
            yield from local_nodes(list(ast.iter_child_nodes(node)))


def body_bindings(
    statements: Sequence[ast.AST],
    inherited: dict[str, str],
    module: dict[str, str],
) -> dict[str, str]:
    """Merge local declarations; conflicting or reassigned names remain unresolved."""
    candidates: dict[str, set[str]] = {}
    global_names: set[str] = set()
    nonlocal_names: set[str] = set()
    for node in local_nodes(statements):
        if isinstance(node, ast.Global):
            global_names.update(node.names)
        elif isinstance(node, ast.Nonlocal):
            nonlocal_names.update(node.names)
        else:
            for name, identity in declared_bindings(node):
                candidates.setdefault(name, set()).add(identity)
    bindings = dict(inherited)
    for name, identities in candidates.items():
        if name not in global_names | nonlocal_names:
            bindings[name] = next(iter(identities)) if len(identities) == 1 else ""
    for name in global_names:
        bindings[name] = module.get(name, "")
    return bindings


def declared_bindings(node: ast.AST) -> Iterator[tuple[str, str]]:
    """Read imports and names that can shadow them in the current scope."""
    if isinstance(node, ast.Import):
        for alias in node.names:
            root = alias.name.split(".", 1)[0]
            yield alias.asname or root, alias.name if alias.asname else root
    elif isinstance(node, ast.ImportFrom):
        for alias in node.names:
            if alias.name != "*":
                yield alias.asname or alias.name, f"{'.' * node.level}{node.module or ''}.{alias.name}"
    elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store | ast.Del):
        yield node.id, ""
    elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef | ast.ExceptHandler) and (
        name := node.name
    ):
        yield name, ""


def lexical_import_bindings(tree: ast.Module) -> dict[ast.AST, dict[str, str]]:
    """Map expressions to lexical aliases; dynamic assignment and control flow are unresolved."""
    module = body_bindings(tree.body, {}, {})
    visitor = BindingVisitor(module)
    visitor.visit(tree)
    return visitor.bindings_by_node


class BindingVisitor(ast.NodeVisitor):
    """Keep function and class imports separate while preserving enclosing aliases."""

    def __init__(self, module: dict[str, str]) -> None:
        """Start at module scope with separate maps for class bodies and method closures."""
        self.module = module
        self.current: dict[str, str] = module
        self.enclosing: dict[str, str] = module
        self.bindings_by_node: dict[ast.AST, dict[str, str]] = {}

    def visit(self, node: ast.AST) -> None:
        """Record the current bindings before visiting one syntax node."""
        self.bindings_by_node[node] = self.current
        super().visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Resolve a function body separately from its defaults and decorators."""
        self.visit_scope(node, node.body)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Resolve an asynchronous function body in its own lexical scope."""
        self.visit_scope(node, node.body)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Resolve class attributes without exposing them as bare names inside methods."""
        self.visit_scope(node, node.body)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        """Keep lambda arguments local while resolving defaults in the enclosing scope."""
        self.visit_scope(node, [node.body])

    def visit_scope(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef | ast.Lambda,
        body: Sequence[ast.AST],
    ) -> None:
        """Visit outer expressions first, then the body with local declarations and arguments."""
        for child in ast.iter_child_nodes(node):
            if child not in body:
                self.visit(child)
        outer, enclosing = self.current, self.enclosing
        local = body_bindings(body, enclosing, self.module)
        if not isinstance(node, ast.ClassDef):
            arguments = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
            for argument in [*arguments, node.args.vararg, node.args.kwarg]:
                if argument is not None:
                    local[argument.arg] = ""
        self.current = local
        if not isinstance(node, ast.ClassDef):
            self.enclosing = local
        for statement in body:
            self.visit(statement)
        self.current, self.enclosing = outer, enclosing

    def visit_ListComp(self, node: ast.ListComp) -> None:
        """Keep list-comprehension targets in their own scope."""
        self.visit_comprehension_scope(node)

    def visit_SetComp(self, node: ast.SetComp) -> None:
        """Keep set-comprehension targets in their own scope."""
        self.visit_comprehension_scope(node)

    def visit_DictComp(self, node: ast.DictComp) -> None:
        """Keep dictionary-comprehension targets in their own scope."""
        self.visit_comprehension_scope(node)

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> None:
        """Keep generator targets in their own scope."""
        self.visit_comprehension_scope(node)

    def visit_comprehension_scope(self, node: ast.ListComp | ast.SetComp | ast.DictComp | ast.GeneratorExp) -> None:
        """Evaluate the first iterable outside the scope, then bind targets before their filters."""
        outer, enclosing = self.current, self.enclosing
        self.visit(node.generators[0].iter)
        self.current = dict(enclosing)
        self.enclosing = self.current
        for index, generator in enumerate(node.generators):
            self.bindings_by_node[generator] = self.current
            if index:
                self.visit(generator.iter)
            self.current = dict(self.current)
            for target in ast.walk(generator.target):
                if isinstance(target, ast.Name):
                    self.current[target.id] = ""
            self.enclosing = self.current
            self.visit(generator.target)
            for condition in generator.ifs:
                self.visit(condition)
        if isinstance(node, ast.DictComp):
            self.visit(node.key)
            self.visit(node.value)
        else:
            self.visit(node.elt)
        self.current, self.enclosing = outer, enclosing
