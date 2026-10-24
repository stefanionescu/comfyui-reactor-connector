"""Read host node schemas and check the node guides against them."""

import os
import sys
import asyncio
from pathlib import Path
import argparse
from contextlib import suppress

from ...src.serialization import Json, parse_json, mapping_value

SCHEMA_TIMEOUT_SECONDS = 60


def host_installation() -> tuple[Path, Path]:
    """Require explicit host selection and return its code directory and Python executable."""
    selected = os.environ.get('COMFYUI_PATH', '')
    if not selected:
        msg = 'Set COMFYUI_PATH to the ComfyUI directory containing main.py and comfy_api.'
        raise ValueError(msg)
    host = Path(selected).expanduser().resolve(strict=True)
    if not (host / 'main.py').is_file() or not (host / 'comfy_api/latest/__init__.py').is_file():
        msg = "COMFYUI_PATH must contain ComfyUI's main.py and comfy_api directory."
        raise ValueError(msg)
    default_python = host / '.venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    interpreter = Path(os.environ.get('COMFYUI_PYTHON', str(default_python))).expanduser().absolute()
    if not interpreter.is_file():
        msg = 'Set COMFYUI_PYTHON to the Python executable used by this ComfyUI installation.'
        raise ValueError(msg)
    return host, interpreter


async def export_schemas(interpreter: Path, root: Path, environment: dict[str, str]) -> bytes:
    """Run the schema export with the host interpreter and return what it prints."""
    process = await asyncio.create_subprocess_exec(
        str(interpreter),
        '-m',
        f'{root.name}.scripts.nodes.schema',
        cwd=root.parent,
        env=environment,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        async with asyncio.timeout(SCHEMA_TIMEOUT_SECONDS):
            stdout, stderr = await process.communicate()
    finally:
        if process.returncode is None:
            with suppress(ProcessLookupError):
                process.kill()
            await process.communicate()
    if process.returncode != 0:
        detail = stderr.decode('utf-8', errors='replace').strip()
        msg = f'The schema export failed with exit status {process.returncode}: {detail}'
        raise RuntimeError(msg)
    return stdout


def read_schemas() -> dict[str, Json]:
    """Read class definitions in a separate process without starting ComfyUI or executing nodes."""
    root = Path(__file__).resolve().parents[2]
    host, interpreter = host_installation()
    environment = dict(os.environ)
    environment['PYTHONPATH'] = os.pathsep.join((str(root.parent), str(host), str(root)))
    output = asyncio.run(export_schemas(interpreter, root, environment))
    # Native dynamic-combo options nest deeper than the shared transport limit.
    return mapping_value(parse_json(output.decode(), max_depth=32))


def validate_metadata(schemas: dict[str, Json]) -> list[str]:
    """Check the node guides against the registered node schemas."""
    root = Path(__file__).resolve().parents[2]
    issues: list[str] = []
    issues.extend(
        f'Use a registered node ID for the guide {path.name}.'
        for path in sorted((root / 'web/docs').glob('*.md'))
        if path.stem not in schemas
    )
    return issues


def main() -> int:
    """Check node registrations and guides against the node schemas."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    issues = validate_metadata(mapping_value(read_schemas()['reactor']))
    for issue in issues:
        sys.stderr.write(issue + '\n')
    return int(bool(issues))


if __name__ == '__main__':
    raise SystemExit(main())
