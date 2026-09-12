"""Validate CodeQL config paths."""

from __future__ import annotations

import yaml
from pathlib import Path
from quality.lib.files import read_utf8
from quality.lib.output import write_error
from quality.lib.json_config import require_mapping, require_string_list


def main() -> int:
    """Validate CodeQL path entries exist."""
    config_path = Path("quality/config/security/codeql/python/scan.yml")
    paths = codeql_paths(read_utf8(config_path))
    violations = [path for path in paths if not Path(path).exists()]
    if not violations:
        return 0
    write_error("CodeQL path violations:")
    for violation in violations:
        write_error(f"- {violation}")
    return 1


def codeql_paths(source_text: str) -> list[str]:
    """Return path entries from the CodeQL YAML config."""
    policy = require_mapping(yaml.safe_load(source_text), "CodeQL configuration")
    paths = require_string_list(policy.get("paths"), "CodeQL paths", are_items_nonempty=True)
    if not paths or any(not path.strip() for path in paths):
        msg = "CodeQL configuration must include a nonempty paths list."
        raise ValueError(msg)
    return paths


if __name__ == "__main__":
    raise SystemExit(main())
