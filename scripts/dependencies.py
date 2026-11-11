"""Export the runtime dependencies used by ComfyUI installers."""

import sys
from typing import cast
from pathlib import Path
import tomllib
import argparse


def requirements(root: Path) -> str:
    """Validate runtime dependency strings and render the ComfyUI installation requirements.

    Args:
        root: The repository folder that holds pyproject.toml.

    Returns:
        The text of the requirements file.

    Raises:
        TypeError: When the dependencies are not a list.
        ValueError: When a dependency is not one nonempty line of text.

    """
    document = tomllib.loads((root / 'pyproject.toml').read_text(encoding='utf-8'))
    raw: object = document['project']['dependencies']
    if not isinstance(raw, list):
        message = 'List runtime dependencies in pyproject.toml.'
        raise TypeError(message)
    dependencies: list[str] = []
    for item in cast('list[object]', raw):
        if not isinstance(item, str) or not item.strip() or any(character in item for character in '\r\n\0'):
            message = 'List each runtime dependency as one nonempty string.'
            raise ValueError(message)
        dependencies.append(item)
    return '# Generated from pyproject.toml by mise run comfy:requirements:build.\n' + ''.join(
        f'{item}\n' for item in dependencies
    )


def main() -> int:
    """Export runtime requirements or report whether the generated file is current.

    Returns:
        The exit status, which is 1 when the generated file is out of date.

    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    destination = root / 'requirements.txt'
    expected = requirements(root)
    if args.check:
        if not destination.is_file() or destination.read_text(encoding='utf-8') != expected:
            sys.stdout.write('Update requirements.txt with mise run comfy:requirements:build.' + '\n')
            return 1
    else:
        destination.write_text(expected, encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
