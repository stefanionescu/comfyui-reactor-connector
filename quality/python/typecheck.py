"""Check connector types against the selected ComfyUI installation."""

from __future__ import annotations

import os
import sys
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from quality.lib.output import write_error
from quality.lib.process import run_command
from quality.lib.json_config import require_string_list


def host_paths() -> list[str]:
    """Read dependency paths from the actual host interpreter without importing ComfyUI."""
    selected = os.environ.get("COMFYUI_PATH", "")
    if not selected:
        msg = "Set COMFYUI_PATH to the ComfyUI directory containing main.py and comfy_api."
        raise ValueError(msg)
    host = Path(selected).expanduser().resolve(strict=True)
    if not (host / "main.py").is_file() or not (host / "comfy_api/latest/__init__.py").is_file():
        msg = "COMFYUI_PATH must contain ComfyUI's main.py and comfy_api directory."
        raise ValueError(msg)
    default_python = host / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    interpreter = Path(os.environ.get("COMFYUI_PYTHON", str(default_python))).expanduser().absolute()
    if not interpreter.is_file():
        msg = "Set COMFYUI_PYTHON to the Python executable used by this ComfyUI installation."
        raise ValueError(msg)
    result = run_command(
        [
            str(interpreter),
            "-I",
            "-c",
            "import json, sysconfig; print(json.dumps([sysconfig.get_path('purelib'), sysconfig.get_path('platlib')]))",
        ],
        is_failure_raised=True,
        is_output_captured=True,
        timeout_seconds=10,
    )
    packages = require_string_list(json.loads(result.stdout), "ComfyUI package directories", is_nonempty=True)
    if not all(Path(item).is_dir() for item in packages):
        msg = "ComfyUI's Python did not report valid package directories."
        raise ValueError(msg)
    return list(dict.fromkeys([str(host), *packages]))


def main() -> int:
    """Run the strict project with actual host dependencies and remove its temporary configuration."""
    root = Path.cwd()
    try:
        search_paths = [str(root), *host_paths()]
        with TemporaryDirectory(prefix="comfyui-reactor-types-") as temporary:
            configuration = Path(temporary) / "pyrightconfig.json"
            configuration.write_text(
                json.dumps({"extends": str(root / "pyrightconfig.json"), "extraPaths": search_paths}),
                encoding="utf-8",
            )
            return run_command(
                ["basedpyright", "--project", str(configuration), *sys.argv[1:]],
                working_directory=root,
            ).return_code
    except (OSError, ValueError, RuntimeError) as error:
        write_error(f"Python type check could not start: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
