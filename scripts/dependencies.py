"""Export the runtime dependencies used by ComfyUI installers."""

import sys
import tomllib
import argparse
from typing import cast
from pathlib import Path


def requirements(root: Path) -> str:
    """Validate runtime dependency strings and render the ComfyUI installation requirements."""
    document = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    raw: object = document["project"]["dependencies"]
    if not isinstance(raw, list):
        msg = "List runtime dependencies in pyproject.toml."
        raise TypeError(msg)
    dependencies: list[str] = []
    for item in cast("list[object]", raw):
        if not isinstance(item, str) or not item.strip() or any(character in item for character in "\r\n\0"):
            msg = "List each runtime dependency as one nonempty string."
            raise ValueError(msg)
        dependencies.append(item)
    return "# Generated from pyproject.toml by mise run deps:export.\n" + "".join(f"{item}\n" for item in dependencies)


def main() -> int:
    """Export runtime requirements or report whether the generated file is current."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    destination = root / "requirements.txt"
    expected = requirements(root)
    if args.check:
        if not destination.is_file() or destination.read_text(encoding="utf-8") != expected:
            sys.stdout.write("Update requirements.txt with mise run deps:export." + "\n")
            return 1
    else:
        destination.write_text(expected, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
