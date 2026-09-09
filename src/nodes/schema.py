"""Apply the native translation file to Python node definitions."""

from typing import cast
from comfy_api.latest import io
from ..language import read_messages


def translate_schema(schema: io.Schema) -> io.Schema:
    """Attach English fallback labels without changing socket IDs, options, or defaults."""
    node = cast("dict[str, object]", read_messages("nodeDefs")[schema.node_id])
    schema.display_name = cast("str", node["display_name"])
    schema.category = cast("str", node["category"])
    schema.search_aliases = cast("list[str]", node["search_aliases"])
    schema.description = cast("str", node["description"])
    inputs = cast("dict[str, dict[str, object]]", node["inputs"])
    outputs = cast("dict[str, dict[str, object]]", node["outputs"])
    for item in schema.inputs:
        labels = inputs[item.id]
        item.display_name = cast("str", labels["name"])
        if "tooltip" in labels:
            item.tooltip = cast("str", labels["tooltip"])
        if isinstance(item, io.String.Input) and "placeholder" in labels:
            item.placeholder = cast("str", labels["placeholder"])
    for index, output in enumerate(schema.outputs):
        labels = outputs[str(index)]
        output.display_name = cast("str", labels["name"])
        if "tooltip" in labels:
            output.tooltip = cast("str", labels["tooltip"])
    return schema
