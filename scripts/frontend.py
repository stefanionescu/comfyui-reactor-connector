"""Build the browser bundle, or check the shipped one."""

import sys
import asyncio
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRY = "web/scripts/extension.ts"
BUNDLE = "extension.js"
STYLES = "extension.css"
HOST_MODULES = ("../../scripts/app.js", "../../scripts/api.js")


async def bundle(destination: Path) -> None:
    """Run esbuild into the given folder."""
    process = await asyncio.create_subprocess_exec(
        "bun",
        "x",
        "esbuild",
        ENTRY,
        f"--outfile={destination / BUNDLE}",
        "--bundle",
        "--platform=browser",
        "--format=esm",
        "--target=es2022",
        "--charset=utf8",
        "--legal-comments=inline",
        *(f"--external:{module}" for module in HOST_MODULES),
        cwd=ROOT,
    )
    if await process.wait() != 0:
        message = "esbuild failed."
        raise RuntimeError(message)


def main() -> int:
    """Build the bundle into web/, or report when the shipped bundle differs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    if not arguments.check:
        asyncio.run(bundle(ROOT / "web"))
        return 0
    scratch = ROOT / ".artifacts" / "frontend"
    scratch.mkdir(parents=True, exist_ok=True)
    asyncio.run(bundle(scratch))
    problems = [
        f"Rebuild {name} with mise run comfy:frontend:build."
        for name in (BUNDLE, STYLES)
        if not (ROOT / "web" / name).is_file() or (ROOT / "web" / name).read_bytes() != (scratch / name).read_bytes()
    ]
    for problem in problems:
        sys.stderr.write(problem + "\n")
    return int(bool(problems))


if __name__ == "__main__":
    raise SystemExit(main())
