"""Scan public source files without printing secret values or inspecting private state."""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import cast

from .repository import visible_files


class SecretCheckError(ValueError):
    """A scanner failure described without values from source or tool output."""


def snapshot(root: Path, destination: Path) -> int:
    """Copy only files visible to Git into an owner-only temporary directory."""
    count = 0
    for source in visible_files(root):
        if source.is_symlink() or not source.resolve().is_relative_to(root):
            raise SecretCheckError(
                "Secret checks require regular source files within the repository."
            )
        if not source.is_file():
            continue
        target = destination / source.relative_to(root)
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with source.open("rb") as incoming, target.open("xb") as stream:
            target.chmod(0o600)
            shutil.copyfileobj(incoming, stream)
        count += 1
    return count


def findings(report: Path, source: Path) -> list[str]:
    """Show only the file, line, and rule; never echo scanner context or values."""
    if not report.is_file() or report.stat().st_size > 4_194_304:
        raise SecretCheckError("The secret scanner did not produce a readable report.")
    value: object = json.loads(report.read_bytes())
    if not isinstance(value, list):
        raise SecretCheckError("The secret scanner returned an invalid report.")
    result: list[str] = []
    for item in cast(list[object], value):
        if not isinstance(item, dict):
            raise SecretCheckError("The secret scanner returned an invalid finding.")
        record = cast(dict[str, object], item)
        file, line, rule = record.get("File"), record.get("StartLine"), record.get("RuleID")
        if not isinstance(file, str) or type(line) is not int or not isinstance(rule, str):
            raise SecretCheckError("The secret scanner returned an incomplete finding.")
        path = Path(file)
        if not path.is_absolute():
            path = source / path
        path = path.resolve()
        if not path.is_relative_to(source):
            raise SecretCheckError(
                "The secret scanner reported a file outside its source snapshot."
            )
        result.append(f"{path.relative_to(source)}:{line}: Review {rule}; value withheld.")
    return result


def main() -> int:
    root = Path.cwd().resolve()
    try:
        with tempfile.TemporaryDirectory(prefix="reactor-source-scan-") as temporary:
            directory = Path(temporary).resolve()
            source = directory / "source"
            source.mkdir(mode=0o700)
            count = snapshot(root, source)
            report = directory / "report.json"
            ignored = directory / "empty-ignore"
            ignored.touch(mode=0o600)
            environment = {
                key: value for key, value in os.environ.items() if not key.startswith("GITLEAKS_")
            }
            result = subprocess.run(
                [
                    "gitleaks",
                    "dir",
                    str(source),
                    "--config",
                    str(root / ".gitleaks.toml"),
                    "--gitleaks-ignore-path",
                    str(ignored),
                    "--ignore-gitleaks-allow",
                    "--redact=100",
                    "--no-banner",
                    "--no-color",
                    "--report-format=json",
                    "--report-path",
                    str(report),
                    "--timeout=60",
                ],
                cwd=directory,
                env=environment,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=65,
                check=False,
            )
            if result.returncode not in (0, 1):
                raise SecretCheckError(
                    "The secret scanner failed. Check the pinned gitleaks installation."
                )
            issues = findings(report, source)
            if result.returncode and not issues:
                raise SecretCheckError("The secret scanner failed without a reportable finding.")
            for issue in issues:
                print(issue)
            if issues:
                return 1
            print(f"Secret scan finished without findings. Source snapshot: {count} files.")
            return 0
    except SecretCheckError as error:
        print(str(error))
        return 1
    except (OSError, ValueError, subprocess.TimeoutExpired):
        print("Secret checking could not finish. Check the tools, configuration, and source files.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
