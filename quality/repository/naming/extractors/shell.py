"""Shell name extraction."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast
from quality.lib.json_config import require_mapping
from quality.shell.parsers import collect_shell_functions, shell_nodes

if TYPE_CHECKING:
    from quality.repository.naming.types import NameCandidate


def extract_shell_names(relative_path: str, source_text: str) -> list[NameCandidate]:
    """Return shell naming candidates."""
    names: list[NameCandidate] = [
        {
            "path": relative_path,
            "line": function["start"],
            "language": "shell",
            "category": "functions",
            "name": function["name"],
        }
        for function in collect_shell_functions(source_text)
    ]
    for node in shell_nodes(source_text):
        if "Name" not in node or node.get("Type") == "FuncDecl":
            continue
        identifier = require_mapping(node["Name"], "shell declaration")
        name = identifier.get("Value")
        if isinstance(name, str):
            position = require_mapping(identifier["Pos"], "declaration position")
            names.append(
                {
                    "path": relative_path,
                    "line": cast("int", position["Line"]),
                    "language": "shell",
                    "category": "variables",
                    "name": name,
                }
            )
    return names
