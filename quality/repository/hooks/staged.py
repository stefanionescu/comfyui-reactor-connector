"""Validate staged content and select the checks it needs."""

from __future__ import annotations

import os
import re
import hashlib
import argparse
from quality.lib.process import run_command
from quality.lib.output import write_error, write_line

SCOPES = {
    "dependencies": rb"^(pyproject\.toml|uv\.lock|requirements\.txt|package\.json|bun\.lock|bunfig\.toml)$",
    "python": rb"^config/|\.pyi?$|^(pyproject\.toml|pyrightconfig\.json|uv\.lock)$|^quality/",
    "frontend": rb"^web/|^scripts/frontend\.mjs$|^(package\.json|bun\.lock|tsconfig\.json|\.stylelintrc\.json)$",
    "hooks": rb"^\.githooks/",
    "mise": rb"^\.mise/|^mise\.toml$",
    "shell": rb"\.sh$|^quality/",
    "quality": rb"^quality/|^rules/|^(AGENTS\.md|mise\.toml|package\.json|bun\.lock|\.gitignore|\.prettier.*)$",
    "docs": rb"\.md$|^web/docs/|^scripts/docs/|^\.markdownlint|^\.typos\.toml$",
    "workflows": rb"^workflows/|^scripts/workflows/",
    "models": rb"^src/discovery/|^config/|^scripts/models\.py$",
}


def git_output(*arguments: str) -> bytes:
    """Read Git output as bytes without interpreting or displaying file contents."""
    result = run_command(["git", *arguments], is_failure_raised=True, is_output_captured=True)
    return result.stdout


def staged_state() -> tuple[str, set[bytes]]:
    """Reject partial staging and return an index fingerprint and staged paths."""
    staged = set(git_output("diff", "--cached", "--name-only", "-z").split(b"\0")) - {b""}
    changed = set(git_output("diff", "--name-only", "-z").split(b"\0")) - {b""}
    if staged & changed:
        msg = "Stage or separate the remaining edits in affected files before committing."
        raise ValueError(msg)
    if git_output("ls-files", "--unmerged", "-z"):
        msg = "Resolve staged merge conflicts before committing."
        raise ValueError(msg)
    fingerprint = hashlib.sha256(git_output("ls-files", "--stage", "-z")).hexdigest()
    return fingerprint, staged


def require_private_files_unstaged(paths: set[bytes]) -> None:
    """Reject private configuration paths even if they were force-added."""
    if os.environ.get("SKIP_ENV_CHECK") == "1":
        write_error("[hook] skipped private file guard (SKIP_ENV_CHECK=1)")
        return
    for path in paths:
        parts = path.split(b"/")
        name = parts[-1]
        if name == b".env" or name.startswith(b".env.") or b".reactor-private" in parts or name == b"PLAN.md":
            msg = "Remove private settings or planning files from staging before committing."
            raise ValueError(msg)


def staged_checks(verify: str | None) -> str | None:
    """Validate private-file staging and return required scopes or verify the checked index."""
    fingerprint, paths = staged_state()
    require_private_files_unstaged(paths)
    if verify:
        if verify != fingerprint:
            msg = "The staged content changed during checks. Run the commit checks again."
            raise ValueError(msg)
        return None
    scopes = [name for name, pattern in SCOPES.items() if any(re.search(pattern, path) for path in paths)]
    return f"{fingerprint} {','.join(scopes) or 'other'}" if paths else "empty none"


def main() -> int:
    """Inspect staged paths or verify that checked content did not change."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", help="The index fingerprint recorded before checks.")
    arguments = parser.parse_args()
    try:
        checks = staged_checks(arguments.verify)
    except (OSError, ValueError, RuntimeError) as error:
        write_error(str(error) if isinstance(error, ValueError) else "Cannot inspect the staged Git content.")
        return 1
    if checks is not None:
        write_line(checks)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
