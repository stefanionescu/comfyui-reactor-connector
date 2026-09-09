"""Validate named example inputs and serialize them in ComfyUI schema order."""

import math
from typing import cast
from collections.abc import Mapping
from ...src.serialization import Json, mapping_value


def widget_values(schema: Json, values: Mapping[str, str | float | bool]) -> list[Json]:
    """Reject missing or unknown widget names before converting values to saved positions."""
    inputs = cast("list[dict[str, Json]]", mapping_value(schema)["inputs"])
    widgets = [item for item in inputs if item["widget"]]
    expected = {str(item["name"]) for item in widgets}
    if any(item.get("control_after_generate") for item in widgets):
        expected.add("control_after_generate")
    if set(values) != expected:
        msg = (
            f"Match widget names to the schema. Missing: {expected - values.keys()}; extra: {values.keys() - expected}."
        )
        raise ValueError(msg)
    result: list[Json] = []
    for item in widgets:
        value = values[str(item["name"])]
        validate_value(item, value=value)
        result.append(float(value) if item["type"] == "FLOAT" else value)
        if item.get("control_after_generate"):
            behavior = values["control_after_generate"]
            if behavior not in {"fixed", "increment", "decrement", "randomize"}:
                msg = "Choose a supported seed behavior for the workflow."
                raise ValueError(msg)
            result.append(behavior)
    return result


def validate_value(item: dict[str, Json], *, value: str | float | bool) -> None:
    """Check widget types, choices, and numeric limits against the registered schema."""
    kind = item["type"]
    valid_type = {
        "STRING": isinstance(value, str),
        "BOOLEAN": isinstance(value, bool),
        "INT": type(value) is int,
        "FLOAT": type(value) in {int, float},
        "COMBO": value in cast("list[Json]", item.get("options", [])),
    }.get(str(kind), False)
    if not valid_type:
        msg = f"Use a valid {kind} value for {item['name']} in the workflow."
        raise ValueError(msg)
    if kind in {"INT", "FLOAT"}:
        number = float(value)
        lower = float(cast("float", item.get("min", -math.inf)))
        upper = float(cast("float", item.get("max", math.inf)))
        if not math.isfinite(number) or not lower <= number <= upper:
            msg = f"Keep {item['name']} within its node's numeric limits."
            raise ValueError(msg)


def validate_sources(schema: Json, sources: tuple[str, ...]) -> None:
    """Require every mandatory media connection and reject unknown source sockets."""
    inputs = cast("list[dict[str, Json]]", mapping_value(schema)["inputs"])
    media = {str(item["name"]): item for item in inputs if not item["widget"]}
    required = {name for name, item in media.items() if not item.get("optional")}
    if set(sources) - media.keys() or required - set(sources):
        msg = "Match the workflow's media sources to the required node sockets."
        raise ValueError(msg)


def validate_connections(nodes: list[Json], schemas: dict[str, Json]) -> None:
    """Reject connected input names or socket types that disagree with a registered node."""
    for value in nodes:
        node = mapping_value(value)
        kind = str(node["type"])
        if kind not in schemas:
            continue
        schema = mapping_value(schemas[kind])
        inputs = {str(item["name"]): item["type"] for item in cast("list[dict[str, Json]]", schema["inputs"])}
        connected = cast("list[dict[str, Json]]", node["inputs"])
        if any(inputs.get(str(item["name"])) != item["type"] for item in connected):
            msg = f"Match connected input names and types to {kind}."
            raise ValueError(msg)
        expected = [item["type"] for item in cast("list[dict[str, Json]]", schema["outputs"])]
        actual = [item["type"] for item in cast("list[dict[str, Json]]", node["outputs"])]
        if actual != expected:
            msg = f"Match saved output sockets to {kind}."
            raise ValueError(msg)


def output_types(schema: Json) -> list[str]:
    """Read socket types from a registered node schema."""
    outputs = mapping_value(schema)["outputs"]
    if not isinstance(outputs, list):
        msg = "Node outputs must be a list."
        raise TypeError(msg)
    return [str(mapping_value(item)["type"]) for item in outputs]
