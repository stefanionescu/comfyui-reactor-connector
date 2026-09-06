"""Export the runtime dependencies used by ComfyUI installers."""

import argparse
import tomllib
from pathlib import Path
from typing import cast


def requirements(root: Path) -> str:
    document = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    raw: object = document["project"]["dependencies"]
    if not isinstance(raw, list):
        raise ValueError("List runtime dependencies in pyproject.toml.")
    dependencies: list[str] = []
    for item in cast(list[object], raw):
        if (
            not isinstance(item, str)
            or not item.strip()
            or any(character in item for character in "\r\n\0")
        ):
            raise ValueError("List each runtime dependency as one nonempty string.")
        dependencies.append(item)
    return "# Generated from pyproject.toml by mise run deps:export.\n" + "".join(
        f"{item}\n" for item in dependencies
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    destination = root / "requirements.txt"
    expected = requirements(root)
    if args.check:
        if not destination.is_file() or destination.read_text(encoding="utf-8") != expected:
            print("Update requirements.txt with mise run deps:export.")
            return 1
    else:
        destination.write_text(expected, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
