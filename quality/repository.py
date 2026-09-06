"""Check source ownership, size, and prohibited repository content."""

import ast
import re
import subprocess
from pathlib import Path

MAX_MODULE_LINES = 300
FORBIDDEN_RUNTIME_IMPORTS = {"quality", "scripts", "tests"}
SECRET_PATTERN = re.compile(r"\brk_[A-Za-z0-9]{20,}\b")


def visible_files(root: Path) -> list[Path]:
    """Use Git's ignore rules and preserve filenames containing spaces."""
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        capture_output=True,
        check=True,
    )
    return sorted({root / name for name in result.stdout.decode().split("\0") if name})


def check_python(path: Path, relative: Path, text: str) -> list[str]:
    """Reject development imports in runtime and oversized source modules."""
    issues: list[str] = []
    tree = ast.parse(text, filename=str(path))
    if len(text.splitlines()) > MAX_MODULE_LINES:
        issues.append(f"{relative}: Split this module by responsibility; it exceeds 300 lines.")
    if "reactor_comfy" not in relative.parts:
        return issues
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
        else:
            continue
        if any(name.split(".")[0] in FORBIDDEN_RUNTIME_IMPORTS for name in names):
            issues.append(f"{relative}:{node.lineno}: Runtime must not import development tools.")
        if (
            any(name.split(".")[0] == "comfy_api" for name in names)
            and not {"nodes", "media"}.intersection(relative.parts)
            and path.name != "extension.py"
        ):
            issues.append(f"{relative}:{node.lineno}: Keep ComfyUI imports at the host boundary.")
    return issues


def check_file(root: Path, path: Path) -> list[str]:
    """Return actionable findings without printing secret values."""
    relative = path.relative_to(root)
    if not path.is_file():
        return []
    if relative.parts[:2] in [(".github", "workflows"), (".gitlab", "workflows")]:
        return [f"{relative}: Use local hooks instead of Git-hosted workflows."]
    if path.name == "Dockerfile" or path.name == ".gitlab-ci.yml":
        return [f"{relative}: This repository does not use deployment or CI files."]
    if path.suffix not in {".py", ".md", ".json", ".toml", ".txt", ".ts", ".js", ".sh"}:
        return []
    text = path.read_text(encoding="utf-8")
    issues: list[str] = []
    if SECRET_PATTERN.search(text):
        issues.append(f"{relative}: Remove the credential; its value is withheld.")
    if path.suffix == ".py":
        issues.extend(check_python(path, relative, text))
    return issues


def main() -> int:
    """Check every tracked or unignored source file."""
    root = Path.cwd()
    issues = [issue for path in visible_files(root) for issue in check_file(root, path)]
    for issue in issues:
        print(issue)
    return int(bool(issues))


if __name__ == "__main__":
    raise SystemExit(main())
