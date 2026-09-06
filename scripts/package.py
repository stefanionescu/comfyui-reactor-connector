"""Build and install a reviewable ComfyUI package without publishing it."""

import argparse
import hashlib
import json
import os
import shutil
import tempfile
import time
import tomllib
import zipfile
from pathlib import Path

from quality.repository import SECRET_PATTERN, visible_files

from .dependencies import requirements

PACKAGE_DIRECTORY = "reactor-inc"
LEGACY_DIRECTORY = "reactor-inc-connector"
ROOT_FILES = (
    "LICENSE.md",
    "__init__.py",
    "pyproject.toml",
    "requirements.txt",
    "README.md",
    "CHANGELOG.md",
    "docs/settings.md",
    "docs/models.md",
    "docs/live.md",
    "docs/development.md",
    "docs/installation.md",
    "docs/troubleshooting.md",
    "docs/recording-details.md",
    "rules/PLAIN_LANGUAGE.md",
)
RUNTIME_DIRECTORIES = (
    "reactor_comfy",
    "web",
    "workflows",
    "docs/nodes",
    "docs/workflows",
    "locales",
)


def package_files(root: Path) -> list[Path]:
    """Include runtime content explicitly and reject linked or private files."""
    public = set(visible_files(root))
    result = [root / name for name in ROOT_FILES]
    if any(path not in public for path in result):
        raise ValueError("Required package files must be included in the public repository.")
    for directory in RUNTIME_DIRECTORIES:
        result.extend(
            path
            for path in public
            if path.is_relative_to(root / directory)
            and path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix != ".pyc"
        )
    for path in result:
        if not path.is_file() or path.is_symlink():
            raise ValueError("Every packaged entry must be an existing regular file.")
        if SECRET_PATTERN.search(path.read_bytes().decode("utf-8", errors="ignore")):
            raise ValueError("A package file contains a credential; the value is withheld.")
    return sorted(result)


def build(root: Path) -> Path:
    """Build a deterministic archive whose manifest identifies every runtime file."""
    if (root / "requirements.txt").read_text(encoding="utf-8") != requirements(root):
        raise ValueError("Update requirements.txt with mise run deps:export before packaging.")
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
                raise ValueError(
                    "Workflow and preview filenames must be unique across model folders."
                )
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
    print(f"Built package {identity[:12]} with {len(contents)} runtime files.")
    return output


def replace_package(extracted: Path, destination: Path, staging: Path, host: Path) -> None:
    """Preserve managed packages and restore their original paths if installation fails."""
    previous = [
        path for path in (destination, destination.parent / LEGACY_DIRECTORY) if path.exists()
    ]
    for path in previous:
        if path.is_symlink() or not (path / ".reactor-package.json").is_file():
            raise ValueError("An existing unmanaged Reactor directory was preserved.")
    backup_root = host.parent / ".reactor-package-backups"
    if previous:
        backup_root.mkdir(mode=0o700, exist_ok=True)
    for path in previous:
        shutil.copytree(path, backup_root / str(time.time_ns()), symlinks=True)
    moved: list[tuple[Path, Path]] = []
    try:
        for path in previous:
            saved = staging / f"previous-{path.name}"
            os.replace(path, saved)
            moved.append((path, saved))
        os.replace(extracted, destination)
    except OSError:
        for original, saved in reversed(moved):
            os.replace(saved, original)
        raise


def install(candidate: Path, host: Path) -> Path:
    """Install this candidate atomically, preserving a prior connector package."""
    if not (host / "main.py").is_file() or not (host / "comfy_api").is_dir():
        raise ValueError("Select the actual ComfyUI source directory.")
    custom_nodes = host / "custom_nodes"
    destination = custom_nodes / PACKAGE_DIRECTORY
    if destination.exists() and not (destination / ".reactor-package.json").is_file():
        raise ValueError("An unmanaged directory already uses this package name; it was preserved.")
    with tempfile.TemporaryDirectory(prefix=".reactor-install-", dir=custom_nodes) as temporary:
        staging = Path(temporary)
        with zipfile.ZipFile(candidate) as archive:
            for info in archive.infolist():
                member = Path(info.filename)
                if (
                    member.is_absolute()
                    or ".." in member.parts
                    or member.parts[0] != PACKAGE_DIRECTORY
                ):
                    raise ValueError("The candidate contains an invalid package path.")
                if info.file_size > 20_000_000:
                    raise ValueError("A candidate file exceeds the installation limit.")
            archive.extractall(staging)
        extracted = staging / PACKAGE_DIRECTORY
        replace_package(extracted, destination, staging, host)
    print("Installed Reactor. Restart ComfyUI to load the updated package.")
    return destination


def main() -> None:
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
