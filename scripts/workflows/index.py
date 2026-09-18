"""Confirm the README links every built workflow so new examples cannot disappear from it."""

from pathlib import Path
from .definitions import EXAMPLES

EXAMPLE_DIRECTORY = "example_workflows"


def readme_issues(root: Path) -> list[str]:
    """Report every example whose file the README does not link."""
    text = (root / "README.md").read_text(encoding="utf-8")
    return [
        f"Link {EXAMPLE_DIRECTORY}/{example.path} from README.md."
        for example in sorted(EXAMPLES, key=lambda item: item.slug)
        if f"({EXAMPLE_DIRECTORY}/{example.path})" not in text
    ]
