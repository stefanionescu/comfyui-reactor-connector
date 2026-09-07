"""Run repository function policy checks."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import TYPE_CHECKING
from quality.lib.languages import source_language
from quality.lib.source import read_python_source
from quality.lib.diagnostics import report_diagnostics
from quality.repository.functions.policy import read_function_policy
from quality.config.repository.paths import FUNCTION_POLICY_EXCLUDED_DIRS
from quality.repository.functions.references import build_repository_functions
from quality.lib.files import git_visible_source_files, read_utf8, staged_files
from quality.repository.functions.shell import collect_shell_function_violations
from quality.repository.functions.python import collect_python_function_violations

if TYPE_CHECKING:
    from collections.abc import Iterable
    from quality.lib.source import PythonSource
    from quality.lib.diagnostics import NamedDiagnostic

type SourceRecord = tuple[str, str, str]


def collect_sources(root: Path, paths: Iterable[str]) -> list[SourceRecord]:
    """Read governed source files from explicit repository-relative paths."""
    records: list[SourceRecord] = []
    for relative_path in paths:
        path = root / relative_path
        if not path.is_file() or any(part in FUNCTION_POLICY_EXCLUDED_DIRS for part in Path(relative_path).parts):
            continue
        source_text = read_utf8(path)
        language = source_language(relative_path, source_text)
        if language is not None:
            records.append((relative_path, source_text, language))
    return records


def python_sources(root: Path, records: list[SourceRecord]) -> list[PythonSource]:
    """Return cached Python source records from governed repository sources."""
    return [
        read_python_source(root, root / relative_path) for relative_path, _, language in records if language == "python"
    ]


def reported_paths(scope: str, root: Path, all_paths: list[str]) -> set[str]:
    """Return paths whose function definitions belong to the reporting scope."""
    if scope == "staged":
        return set(staged_files(root=root, is_existing_required=True))
    return {path for path in all_paths if path_in_scope(path, scope)}


def path_in_scope(relative_path: str, scope: str) -> bool:
    """Return whether a repository path belongs to one function-policy scope."""
    if scope in {"", "all"}:
        return True
    if scope == "python":
        return relative_path.endswith(".py")
    if scope == "shell":
        return relative_path.endswith(".sh") or relative_path.startswith((".githooks/", ".mise/tasks/"))
    return any(relative_path.startswith(f"{part.strip().rstrip('/')}/") for part in scope.split(",") if part.strip())


def analyze_functions(scope: str, root: Path) -> list[NamedDiagnostic]:
    """Return function-policy violations with repository-wide reference counts."""
    policy = read_function_policy(root)
    all_paths = git_visible_source_files(root=root, is_existing_required=True)
    records = collect_sources(root, all_paths)
    sources = python_sources(root, records)
    repository = build_repository_functions(sources)
    selected_paths = reported_paths(scope, root, all_paths)
    source_by_path = {source.relative_path: source for source in sources}

    errors: list[NamedDiagnostic] = []
    for relative_path, source_text, language in records:
        if relative_path not in selected_paths:
            continue
        if language == "python":
            source = source_by_path[relative_path]
            errors.extend(collect_python_function_violations(source, policy["python"], repository))
        elif language == "shell":
            errors.extend(collect_shell_function_violations(relative_path, source_text, policy["shell"]))
    return errors


def main() -> int:
    """Run function policy checks."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", default="all")
    arguments = parser.parse_args()
    errors = analyze_functions(arguments.scope, Path.cwd())
    return report_diagnostics("Function policy violations:", errors)


if __name__ == "__main__":
    raise SystemExit(main())
