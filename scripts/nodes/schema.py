"""Export registered node schemas without starting ComfyUI or executing nodes."""

import sys
import json
import inspect
from comfy_api.latest import io
from ...src.extension import NODE_REGISTRATIONS
from ...config.models.identities import MODELS


def main() -> None:
    """Describe the real node inputs and reject incomplete or conflicting registrations."""
    schemas = {}
    for node, model in NODE_REGISTRATIONS.items():
        schema = node.define_schema()
        if schema.node_id in schemas or model not in MODELS:
            msg = "Each node must have a unique ID and a known model."
            raise ValueError(msg)
        # ComfyUI leaves the base execution callable untyped; inspect only its declared names.
        parameters = set(inspect.signature(node.execute).parameters)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType] -- reason: The host base class leaves execute untyped; only its signature is inspected.
        if parameters != {item.id for item in schema.inputs}:
            msg = f"Align the schema and execution inputs for {schema.node_id}."
            raise ValueError(msg)
        schemas[schema.node_id] = {
            "model": model,
            "inputs": [
                {
                    "name": item.id,
                    "type": item.io_type,
                    "widget": isinstance(item, io.WidgetInput),
                    **item.as_dict(),
                }
                for item in schema.inputs
            ],
            "outputs": [{"type": item.io_type, **item.as_dict()} for item in schema.outputs],
        }
    sys.stdout.write(json.dumps(schemas, indent=2) + "\n")


if __name__ == "__main__":
    main()
