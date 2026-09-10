"""Read host node schemas and validate registrations and translations."""

import os
import sys
import argparse
from pathlib import Path
from ...config.models.nodes import NODE_MODELS
from .translations import validate_translations
from ...quality.lib.comfy import host_installation
from ...quality.lib.process import ProcessContext, run_command
from ...src.serialization import Json, parse_json, mapping_value


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
    return mapping_value(parse_json(result.stdout.decode()))


def validate_metadata(schemas: dict[str, Json]) -> list[str]:
    """Check registered model associations and their language resources."""
    models = {node_id: mapping_value(schema)["model"] for node_id, schema in schemas.items()}
    if models != NODE_MODELS:
        return ["Align model associations with the registered node classes."]
    root = Path(__file__).resolve().parents[2]
    return validate_translations(root / "locales", schemas)


def main() -> int:
    """Check node registrations and translations against the node schemas."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    issues = validate_metadata(read_schemas())
    for issue in issues:
        sys.stderr.write(issue + "\n")
    return int(bool(issues))


if __name__ == "__main__":
    raise SystemExit(main())
