"""Build native ComfyUI help from the authored node guides."""

import sys
import argparse
from pathlib import Path
from .pages import HelpPages
from ...config.models.nodes import NODE_MODELS


def inventory_issues(source: Path, output: Path, expected: set[str]) -> list[str]:
    """Require a guide for every public node and reject orphaned generated help."""
    authored = {path.stem for path in source.glob("*.md")}
    generated = {path.stem for path in output.glob("*.md")}
    issues = [f"Write node help for {name}." for name in sorted(expected - authored)]
    issues.extend(f"Remove or register orphaned node help for {name}." for name in sorted(authored - expected))
    issues.extend(f"Remove stale generated node help for {name}." for name in sorted(generated - expected))
    return issues


def build_help(root: Path, generated: dict[Path, bytes], *, check: bool) -> list[str]:
    """Write or compare generated help and remove stale HTML guide files."""
    issues: list[str] = []
    for path, content in generated.items():
        if check:
            if not path.exists() or path.read_bytes() != content:
                issues.append(f"Rebuild help page {path.name}.")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    for path in (root / "web/dist/guides").rglob("*"):
        if not path.is_file() or path in generated:
            continue
        if check:
            issues.append(f"Remove stale help page {path.name}.")
        else:
            path.unlink()
    return issues


def main() -> int:
    """Build or verify native node help and linked HTML guides from their authored sources."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    source = root / "web" / "docs"
    output = root / "web" / "dist" / "docs"
    issues = inventory_issues(source, output, set(NODE_MODELS))
    if not issues:
        pages = HelpPages(root)
        generated = pages.build()
        generated.update({output / guide.name: pages.markdown(guide) for guide in source.glob("*.md")})
        issues.extend(build_help(root, generated, check=args.check))
    for issue in issues:
        sys.stdout.write(issue + "\n")
    return int(bool(issues))


if __name__ == "__main__":
    raise SystemExit(main())
