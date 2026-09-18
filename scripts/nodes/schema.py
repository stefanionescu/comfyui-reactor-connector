"""Export registered node schemas without starting ComfyUI or executing nodes."""

import sys
import json
import inspect
from comfy_api.latest import io
from ...src.models import MODELS
from ...src.nodes.base import VideoNode
from ...src.extension import NODE_REGISTRATIONS
from .native import describe_schema, native_schemas

CATEGORIES = {f"Reactor/{group}" for group in ("Generate", "Edit", "Live", "Worlds", "Plans")}


def read_input_names(node: type[io.ComfyNode]) -> set[str]:
    """Read the names a node's entry point receives; video nodes take the run number through their base."""
    if issubclass(node, VideoNode):
        return {"variation", *inspect.signature(node.generate).parameters}
    return set(inspect.signature(node.execute).parameters)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType] -- reason: The host base class leaves execute untyped; only its signature is inspected.


def main() -> None:
    """Describe the real node inputs and reject incomplete or conflicting registrations."""
    schemas = {}
    for node, model in NODE_REGISTRATIONS.items():
        schema = node.define_schema()
        if schema.node_id in schemas or model not in MODELS:
            msg = "Each node must have a unique ID and a known model."
            raise ValueError(msg)
        parameters = read_input_names(node)
        if parameters != {item.id for item in schema.inputs}:
            msg = f"Align the schema and execution inputs for {schema.node_id}."
            raise ValueError(msg)
        if not schema.display_name or not schema.description or schema.category not in CATEGORIES:
            msg = f"Declare a display name, description, and Reactor category for {schema.node_id}."
            raise ValueError(msg)
        schemas[schema.node_id] = {"model": model, **describe_schema(schema)}
    sys.stdout.write(json.dumps({"reactor": schemas, "native": native_schemas()}, indent=2) + "\n")


if __name__ == "__main__":
    main()
