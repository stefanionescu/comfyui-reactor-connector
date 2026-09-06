"""Check the staged content without changing the user's index or worktree."""

import subprocess
import sys


def paths(arguments: list[str]) -> set[bytes]:
    """Read NUL-delimited Git paths without shell interpretation."""
    result = subprocess.run(["git", *arguments], capture_output=True, check=True)
    return {entry for entry in result.stdout.split(b"\0") if entry}


def main() -> int:
    """Reject partial staging, then run the local gate against matching content."""
    staged = paths(["diff", "--cached", "--name-only", "-z"])
    if not staged:
        return 0
    changed = paths(["diff", "--name-only", "-z"])
    if staged & changed:
        print("Stage or separate the remaining edits in affected files before committing.")
        return 1
    return subprocess.run(["mise", "run", "check"], check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
