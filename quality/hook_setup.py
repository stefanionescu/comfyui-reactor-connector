"""Install this repository's hooks without replacing existing user behavior."""

import subprocess
from pathlib import Path

HOOKS = ("pre-commit", "commit-msg", "pre-push")


def setup(root: Path) -> None:
    configured = subprocess.run(
        ["git", "config", "--get", "core.hooksPath"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    current = configured.stdout.strip()
    target = root / ".githooks"
    if configured.returncode not in (0, 1):
        raise ValueError("Cannot read this repository's Git hook configuration.")
    if current and (root / current).resolve() != target.resolve():
        raise ValueError(
            "Existing Git hooks were preserved. Review their integration before setup."
        )
    if not current:
        directory = subprocess.run(
            ["git", "rev-parse", "--git-path", "hooks"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        if any((root / directory / name).exists() for name in HOOKS):
            raise ValueError(
                "Existing Git hooks were preserved. Review their integration before setup."
            )
    paths = [target / name for name in HOOKS]
    if any(not path.is_file() or path.is_symlink() for path in paths):
        raise ValueError("Restore the three regular hook files before setup.")
    for path in paths:
        path.chmod(path.stat().st_mode | 0o111)
    subprocess.run(
        ["git", "config", "--local", "core.hooksPath", ".githooks"], cwd=root, check=True
    )


def main() -> int:
    try:
        root = Path(
            subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
        )
        setup(root)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(str(error) if isinstance(error, ValueError) else "Git hook setup failed.")
        return 1
    print("Configured this repository's three local Git hooks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
