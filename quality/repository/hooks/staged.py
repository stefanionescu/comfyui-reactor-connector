"""Keep private settings and credentials out of commits."""

import os
from collections.abc import Iterable
from quality.lib.files import staged_files
from quality.lib.output import write_error


def require_private_files_unstaged(paths: Iterable[str]) -> None:
    """Reject private configuration paths even if they were force-added."""
    if os.environ.get("SKIP_ENV_CHECK") == "1":
        write_error("[hook] skipped private file guard (SKIP_ENV_CHECK=1)")
        return
    for path in paths:
        parts = path.split("/")
        name = parts[-1]
        if name == ".env" or name.startswith(".env.") or ".reactor-private" in parts:
            msg = "Remove private settings or credentials from staging before committing."
            raise ValueError(msg)


def main() -> int:
    """Reject private file paths in the staged changes."""
    try:
        require_private_files_unstaged(staged_files())
    except (OSError, ValueError, RuntimeError) as error:
        write_error(str(error) if isinstance(error, ValueError) else "Cannot inspect the staged Git content.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
