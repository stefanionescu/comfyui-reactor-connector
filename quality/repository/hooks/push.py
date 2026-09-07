"""Require push checks to inspect the exact revision Git will send."""

from __future__ import annotations

import re
import argparse
from pathlib import Path
from quality.lib.output import write_error, write_line
from quality.repository.hooks.staged import git_output


MAX_PUSH_INPUT_BYTES = 1_048_576
PUSH_FIELD_COUNT = 4


def pushed_commits(path: Path) -> set[bytes]:
    """Read bounded Git pre-push records and ignore ref deletions."""
    with path.open("rb") as stream:
        payload = stream.read(1_048_577)
    if len(payload) > MAX_PUSH_INPUT_BYTES:
        msg = "The pre-push revision list is too large."
        raise ValueError(msg)
    commits: set[bytes] = set()
    for line in payload.splitlines():
        fields = line.split()
        if len(fields) != PUSH_FIELD_COUNT or not re.fullmatch(rb"[0-9a-f]{40}|[0-9a-f]{64}", fields[1]):
            msg = "Git supplied an invalid pre-push revision record."
            raise ValueError(msg)
        if set(fields[1]) != {ord("0")}:
            commits.add(fields[1])
    return commits


def require_clean_head() -> bytes:
    """Return HEAD only when tracked and public untracked files are clean."""
    head = git_output("rev-parse", "HEAD").strip()
    if git_output("status", "--porcelain=v1", "-z"):
        msg = "Make the worktree clean before running push checks."
        raise ValueError(msg)
    return head


def push_revision(records: Path | None, verify: str | None) -> str | None:
    """Require an unchanged checked revision or return the exact commit being pushed."""
    if verify:
        if require_clean_head().decode("ascii") != verify:
            msg = "The checked revision changed. Run the push checks again."
            raise ValueError(msg)
        return None
    if records is None:
        msg = "Provide the Git pre-push records file."
        raise ValueError(msg)
    commits = pushed_commits(records)
    if not commits:
        return "deleted"
    head = require_clean_head()
    if commits != {head}:
        msg = "Check out the revision being pushed before running push checks."
        raise ValueError(msg)
    return head.decode("ascii")


def main() -> int:
    """Validate push records before checks and recheck the revision afterward."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records", nargs="?", type=Path)
    parser.add_argument("--verify", help="The revision recorded before checks.")
    arguments = parser.parse_args()
    try:
        revision = push_revision(arguments.records, arguments.verify)
    except (OSError, ValueError, RuntimeError) as error:
        write_error(str(error) if isinstance(error, ValueError) else "Cannot validate the Git push revision.")
        return 1
    if revision is not None:
        write_line(revision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
