"""Build native ComfyUI help from the authored node guides."""

import argparse
from pathlib import Path

from reactor_comfy.node_catalog import NODE_MODELS

from .help_pages import HelpPages


def inventory_issues(source: Path, output: Path) -> list[str]:
    """Require a guide for every public node and reject orphaned generated help."""
    expected = set(NODE_MODELS)
    authored = {path.stem for path in source.glob("*.md")}
    generated = {path.stem for path in output.glob("*.md")}
    issues = [f"Write node help for {name}." for name in sorted(expected - authored)]
    issues.extend(
        f"Remove or register orphaned node help for {name}." for name in sorted(authored - expected)
    )
    issues.extend(
        f"Remove stale generated node help for {name}." for name in sorted(generated - expected)
    )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    source = root / "docs" / "nodes"
    output = root / "web" / "docs"
    issues = inventory_issues(source, output)
    if issues:
        for issue in issues:
            print(issue)
        return 1
    pages = HelpPages(root)
    generated = pages.build()
    for guide in source.glob("*.md"):
        target = output / guide.name
        data = pages.markdown(guide)
        if args.check:
            if not target.exists() or target.read_bytes() != data:
                issues.append(f"Rebuild native help for {guide.stem}.")
        else:
            output.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    for path, data in generated.items():
        if args.check:
            if not path.exists() or path.read_bytes() != data:
                issues.append(f"Rebuild help page {path.name}.")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    for path in (root / "web/guides").rglob("*"):
        if path.is_file() and path not in generated:
            if args.check:
                issues.append(f"Remove stale help page {path.name}.")
            else:
                path.unlink()
    for issue in issues:
        print(issue)
    return int(bool(issues))


if __name__ == "__main__":
    raise SystemExit(main())
