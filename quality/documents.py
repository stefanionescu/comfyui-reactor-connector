"""Check local Markdown references without claiming a plain-language assessment."""

import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

from .repository import visible_files


def check_document(path: Path, text: str) -> list[str]:
    """Find broken local file links and whitespace that obscures review."""
    issues: list[str] = []
    for number, line in enumerate(text.splitlines(), 1):
        if line.rstrip() != line:
            issues.append(f"{path.name}:{number}: Remove trailing whitespace.")
    if not text.endswith("\n"):
        issues.append(f"{path.name}: End the document with a newline.")
    for match in re.finditer(r"\]\(([^)]+)\)", text):
        target = match.group(1)
        parts = urlsplit(target.strip("<>"))
        if parts.scheme or not parts.path or parts.path.startswith("/"):
            continue
        destination = path.parent / unquote(parts.path)
        if not destination.exists():
            issues.append(f"{path.name}: Repair the local link to {parts.path}.")
    return issues


def main() -> int:
    """Check documentation files visible to Git."""
    issues = [
        issue
        for path in visible_files(Path.cwd())
        if path.is_file() and path.suffix == ".md"
        for issue in check_document(path, path.read_text())
    ]
    for issue in issues:
        print(issue)
    return int(bool(issues))


if __name__ == "__main__":
    raise SystemExit(main())
