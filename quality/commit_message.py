"""Check commit subjects without rejecting Git's generated maintenance messages."""

import argparse
import re
from pathlib import Path

from .repository import SECRET_PATTERN

SUBJECT = re.compile(
    r"(?:feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(?:\([a-z0-9][a-z0-9_./-]*\))?!?: \S.*"
)


def valid_subject(subject: str) -> bool:
    """Accept conventional subjects and recognizable Git-generated subjects."""
    if any(ord(character) < 32 for character in subject):
        return False
    if SUBJECT.fullmatch(subject):
        return True
    if re.fullmatch(r'Revert ".+"', subject):
        return True
    if re.fullmatch(
        r"Merge (?:branch|branches|remote-tracking branch|tag|pull request) .+", subject
    ):
        return True
    return any(
        subject.startswith(prefix) and subject[len(prefix) :].strip()
        for prefix in ("fixup! ", "squash! ", "amend! ")
    )


def check_message(text: str) -> str | None:
    if SECRET_PATTERN.search(text):
        return "Remove the credential from the commit message; its value is withheld."
    subject = next(
        (line for line in text.splitlines() if line.strip() and not line.startswith("#")), ""
    )
    if not valid_subject(subject):
        return (
            "Use a subject such as 'fix(video): preserve source timing'. See docs/development.md."
        )
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("message_file", type=Path)
    args = parser.parse_args()
    try:
        with args.message_file.open("rb") as stream:
            data = stream.read(262_145)
        if len(data) > 262_144:
            raise ValueError
        issue = check_message(data.decode())
    except (OSError, ValueError):
        issue = "Provide a readable UTF-8 commit message under 256 KiB."
    if issue:
        print(issue)
    return int(issue is not None)


if __name__ == "__main__":
    raise SystemExit(main())
