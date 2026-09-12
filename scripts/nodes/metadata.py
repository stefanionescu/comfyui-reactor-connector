"""Read host node schemas and validate registrations and translations."""

import os
import sys
import argparse
from pathlib import Path
from ...src.state.documents import Json
from .translations import validate_translations
from ...quality.lib.comfy import host_installation
from ...src.serialization import parse_json, mapping_value
from ...quality.lib.process import ProcessContext, run_command


def read_schemas() -> dict[str, Json]:
    """Read class definitions in a separate process without starting ComfyUI or executing nodes."""
    root = Path(__file__).resolve().parents[2]
    host, interpreter = host_installation()
    environment = dict(os.environ)
    environment["PYTHONPATH"] = os.pathsep.join((str(root.parent), str(host), str(root)))
    result = run_command(
        [str(interpreter), "-m", f"{root.name}.scripts.nodes.schema"],
        is_output_captured=True,
        is_failure_raised=True,
        context=ProcessContext(working_directory=root.parent, timeout_seconds=60, environment=environment),
    )
    # Native dynamic-combo options nest deeper than the shared transport limit.
    return mapping_value(parse_json(result.stdout.decode(), max_depth=32))


def validate_metadata(schemas: dict[str, Json]) -> list[str]:
    """Check supplied language resources against registered node schemas."""
    root = Path(__file__).resolve().parents[2]
    issues = validate_translations(root / "locales", schemas)
    issues.extend(
        f"Use a registered node ID for the guide {path.name}."
        for path in sorted((root / "web/docs").glob("*.md"))
        if path.stem not in schemas
    )
    return issues


def main() -> int:
    """Check node registrations and translations against the node schemas."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    issues = validate_metadata(mapping_value(read_schemas()["reactor"]))
    for issue in issues:
        sys.stderr.write(issue + "\n")
    return int(bool(issues))


if __name__ == "__main__":
    raise SystemExit(main())
