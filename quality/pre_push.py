"""Check the revision Git intends to push against a clean, matching worktree."""

import re
import subprocess
import sys


def pushed_commits(text: str) -> set[str]:
    """Ignore ref deletion while validating every supplied revision identifier."""
    commits: set[str] = set()
    for line in text.splitlines():
        fields = line.split()
        if len(fields) != 4 or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", fields[1]):
            raise ValueError("Git supplied an invalid pre-push revision record.")
        if set(fields[1]) != {"0"}:
            commits.add(fields[1])
    return commits


def git(*arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments], capture_output=True, text=True, check=True
    ).stdout.strip()


def main() -> int:
    try:
        data = sys.stdin.read(1_048_577)
        if len(data) > 1_048_576:
            raise ValueError("The pre-push revision list is too large.")
        commits = pushed_commits(data)
        if not commits:
            return 0
        head = git("rev-parse", "HEAD")
        if commits != {head} or git("status", "--porcelain=v1", "-z"):
            raise ValueError(
                "Check out the revision being pushed and make the worktree clean first."
            )
        result = subprocess.run(["mise", "run", "check"], check=False)
        if result.returncode:
            return result.returncode
        if git("rev-parse", "HEAD") != head or git("status", "--porcelain=v1", "-z"):
            raise ValueError(
                "The checked revision changed during validation. Run the push checks again."
            )
        print(f"Validated push revision {head} with a clean worktree.")
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(
            str(error)
            if isinstance(error, ValueError)
            else "Cannot validate the Git push revision."
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
