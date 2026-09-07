"""Select public files for documentation and package builds."""

import re
from pathlib import Path
from quality.lib.process import run_command

SECRET_PATTERN = re.compile(r"\brk_[A-Za-z0-9]{20,}\b")


def visible_files(root: Path) -> list[Path]:
    """Use Git's ignore rules and preserve filenames containing spaces."""
    result = run_command(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        working_directory=root,
        is_output_captured=True,
        is_failure_raised=True,
    )
    return sorted({root / name for name in result.stdout.decode().split("\0") if name})
