"""Audit locked Python dependencies without installing or running their code."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

from packaging.requirements import InvalidRequirement, Requirement


def locked_requirements(root: Path) -> str:
    """Export exact pins and reject URLs or resolver options before querying PyPI."""
    result = subprocess.run(
        [
            "uv",
            "export",
            "--offline",
            "--frozen",
            "--all-groups",
            "--no-emit-project",
            "--no-header",
            "--no-hashes",
            "--format",
            "requirements-txt",
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    if result.returncode:
        raise ValueError("Export the locked Python dependencies before auditing them.")
    lines: list[str] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            requirement = Requirement(line)
        except InvalidRequirement:
            raise ValueError("The audit needs named packages with exact version pins.") from None
        pins = list(requirement.specifier)
        if requirement.url or len(pins) != 1 or pins[0].operator != "==" or "*" in pins[0].version:
            raise ValueError("The audit needs registry packages with exact version pins.")
        lines.append(line)
    if not lines:
        raise ValueError("The lockfile contains no dependencies to audit.")
    return "\n".join(lines) + "\n"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    environment = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("REACTOR_", "PIP_AUDIT_"))
    }
    try:
        requirements = locked_requirements(root)
        with tempfile.TemporaryDirectory(prefix="reactor-dependency-audit-") as directory:
            path = Path(directory) / "requirements.txt"
            path.write_text(requirements, encoding="utf-8")
            path.chmod(0o600)
            print(
                "Audit scope: locked Python dependencies for this platform, "
                "including development tools. Querying PyPI advisories.",
                flush=True,
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip_audit",
                    "--requirement",
                    str(path),
                    "--no-deps",
                    "--disable-pip",
                    "--strict",
                    "--vulnerability-service",
                    "pypi",
                    "--progress-spinner",
                    "off",
                    "--timeout",
                    "15",
                ],
                cwd=root,
                env=environment,
                check=False,
                timeout=120,
            )
            return result.returncode
    except (OSError, ValueError, subprocess.TimeoutExpired):
        print("The dependency audit could not finish. Check the lockfile, tools, and network.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
