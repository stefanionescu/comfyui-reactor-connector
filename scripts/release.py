"""Build and install a reviewable ComfyUI package without publishing it."""

import re
import sys
import json
import time
import shutil
import hashlib
import tomllib
import zipfile
import argparse
import tempfile
from pathlib import Path
from .dependencies import requirements
from ..quality.lib.process import run_command
from ..config.security import REACTOR_KEY_PATTERN
from ..quality.lib.files import git_visible_files


MAX_ARCHIVE_MEMBER_BYTES = 20_000_000

PACKAGE_DIRECTORY = "reactor-inc"
ROOT_FILES = (
    "LICENSE.md",
    "__init__.py",
    "__main__.py",
    "pyproject.toml",
    "requirements.txt",
    "README.md",
    "ADVANCED.md",
)
RUNTIME_DIRECTORIES = ("src", "config", "web/dist", "workflows", "locales")


def package_files(root: Path) -> list[Path]:
    """Include runtime content explicitly and reject linked or private files."""
    public = {root / name for name in git_visible_files(root=root, is_existing_required=True)}
    result = [root / name for name in ROOT_FILES]
    if any(path not in public for path in result):
        msg = "Required package files must be included in the public repository."
        raise ValueError(msg)
    for directory in RUNTIME_DIRECTORIES:
        result.extend(
            path
            for path in public
            if path.is_relative_to(root / directory)
            and path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix not in {".pyc", ".ts"}
        )
    for path in result:
        if not path.is_file() or path.is_symlink():
            msg = "Every packaged entry must be an existing regular file."
            raise ValueError(msg)
        if re.search(REACTOR_KEY_PATTERN, path.read_bytes().decode("utf-8", errors="ignore")):
            msg = "A package file contains a credential; the value is withheld."
            raise ValueError(msg)
    return sorted(result)


def build(root: Path) -> Path:
    """Build a deterministic archive whose manifest identifies every runtime file."""
    if (root / "requirements.txt").read_text(encoding="utf-8") != requirements(root):
        msg = "Update requirements.txt with mise run deps:export before packaging."
        raise ValueError(msg)
    files = package_files(root)
    version = tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"]
    contents = {path.relative_to(root).as_posix(): path.read_bytes() for path in files}
    # ComfyUI lists only top-level templates; keep the grouped originals for direct use.
    for path in files:
        if path.is_relative_to(root / "workflows") and (
            path.suffix == ".json" or (path.suffix == ".jpg" and path.with_suffix(".json") in files)
        ):
            name = f"workflows/{path.name}"
            if name in contents:
                msg = "Workflow and preview filenames must be unique across model folders."
                raise ValueError(msg)
            contents[name] = path.read_bytes()
    manifest = {name: hashlib.sha256(content).hexdigest() for name, content in contents.items()}
    encoded_manifest = json.dumps(manifest, sort_keys=True).encode()
    identity = hashlib.sha256(encoded_manifest).hexdigest()
    output = root / "dist" / f"{PACKAGE_DIRECTORY}-{version}-{identity[:12]}.zip"
    output.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in sorted(contents.items()):
            archive.writestr(zipfile.ZipInfo(f"{PACKAGE_DIRECTORY}/{name}"), content)
        archive.writestr(
            zipfile.ZipInfo(f"{PACKAGE_DIRECTORY}/.reactor-package.json"),
            json.dumps({"identity": identity, "files": manifest}, indent=2),
        )
    scan_archive(root, output)
    sys.stdout.write(f"Built package {identity[:12]} with {len(contents)} runtime files." + "\n")
    return output


def scan_archive(root: Path, candidate: Path) -> None:
    """Require a redacted secret scan of the actual archive before installation."""
    report = root / ".artifacts/security/gitleaks/archive.json"
    report.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    report.touch(mode=0o600, exist_ok=True)
    report.chmod(0o600)
    command = [
        "gitleaks",
        "dir",
        str(candidate),
        "--config",
        str(root / "quality/config/security/gitleaks/config.toml"),
        "--report-format",
        "json",
        "--report-path",
        str(report),
        "--max-archive-depth",
        "3",
        "--no-banner",
        "--redact",
        "--ignore-gitleaks-allow",
    ]
    try:
        run_command(command, is_failure_raised=True)
    except (OSError, RuntimeError):
        candidate.unlink(missing_ok=True)
        msg = "The release secret scan failed. No package was installed."
        raise ValueError(msg) from None


def replace_package(extracted: Path, destination: Path, staging: Path, host: Path) -> None:
    """Preserve the managed package and restore it if installation fails."""
    saved = staging / "previous"
    if destination.exists():
        if destination.is_symlink() or not (destination / ".reactor-package.json").is_file():
            msg = "An existing unmanaged Reactor directory was preserved."
            raise ValueError(msg)
        backup_root = host.parent / ".reactor-package-backups"
        backup_root.mkdir(mode=0o700, exist_ok=True)
        shutil.copytree(destination, backup_root / str(time.time_ns()), symlinks=True)
        destination.replace(saved)
    try:
        extracted.replace(destination)
    except OSError:
        if saved.exists():
            saved.replace(destination)
        raise


def install(candidate: Path, host: Path) -> Path:
    """Install this candidate atomically, preserving a prior connector package."""
    if not (host / "main.py").is_file() or not (host / "comfy_api").is_dir():
        msg = "Select the actual ComfyUI source directory."
        raise ValueError(msg)
    installation_root = host / "custom_nodes"
    destination = installation_root / PACKAGE_DIRECTORY
    if destination.exists() and not (destination / ".reactor-package.json").is_file():
        msg = "An unmanaged directory already uses this package name; it was preserved."
        raise ValueError(msg)
    with tempfile.TemporaryDirectory(prefix=".reactor-install-", dir=installation_root) as temporary:
        staging = Path(temporary)
        with zipfile.ZipFile(candidate) as archive:
            for entry in archive.infolist():
                member = Path(entry.filename)
                if member.is_absolute() or ".." in member.parts or member.parts[0] != PACKAGE_DIRECTORY:
                    msg = "The candidate contains an invalid package path."
                    raise ValueError(msg)
                if entry.file_size > MAX_ARCHIVE_MEMBER_BYTES:
                    msg = "A candidate file exceeds the installation limit."
                    raise ValueError(msg)
            archive.extractall(staging)
        extracted = staging / PACKAGE_DIRECTORY
        replace_package(extracted, destination, staging, host)
    sys.stdout.write("Installed Reactor. Restart ComfyUI to load the updated package." + "\n")
    return destination


def main() -> None:
    """Build the release archive and install it only when a host directory is supplied."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", type=Path)
    parser.add_argument("--install", action="store_true", help="Require a ComfyUI host directory.")
    args = parser.parse_args()
    if args.install and args.host is None:
        parser.error("Provide --host with the ComfyUI directory to install the package.")
    root = Path(__file__).resolve().parents[1]
    candidate = build(root)
    if args.host:
        install(candidate, args.host)


if __name__ == "__main__":
    main()
