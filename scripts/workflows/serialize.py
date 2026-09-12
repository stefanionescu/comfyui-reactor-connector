"""Validate named example inputs and serialize them in ComfyUI schema order."""

import math
from typing import cast
from collections.abc import Mapping
from ...src.state.documents import Json
from ...src.serialization import mapping_value


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


def native_widget_values(kind: str, schema: Json, filename_prefix: str = "") -> list[Json]:
    """Check the four native node contracts used by these examples before serialization."""
    inputs = [mapping_value(item) for item in cast("list[Json]", mapping_value(schema)["inputs"])]
    expected = {
        "LoadImage": ["image"],
        "LoadVideo": ["file"],
        "SaveVideo": ["video", "filename_prefix", "format", "codec"],
        "SaveAudioAdvanced": ["audio", "filename_prefix", "format"],
    }
    if [item["name"] for item in inputs] != expected[kind]:
        msg = f"Inspect the changed native input order for {kind}."
        raise ValueError(msg)
    if kind in {"LoadImage", "LoadVideo"}:
        if inputs[0]["type"] != "COMBO":
            msg = f"Inspect the changed upload input for {kind}."
            raise ValueError(msg)
        return ["", "image"]
    selected = "auto" if kind == "SaveVideo" else "flac"
    options = cast("list[Json]", inputs[2]["options"])
    choice = mapping_value(options[0])
    if inputs[2]["type"] != "COMFY_DYNAMICCOMBO_V3" or choice["key"] != selected:
        msg = f"Inspect the changed native format selection for {kind}."
        raise ValueError(msg)
    if kind == "SaveAudioAdvanced":
        if any(mapping_value(choice["inputs"]).values()):
            msg = "Inspect the changed FLAC widget controls."
            raise ValueError(msg)
        return [filename_prefix, "flac"]
    validate_video_codec(inputs[3], choice)
    return [filename_prefix, "auto", "auto", "auto"]


def validate_video_codec(codec: Json, choice: Json) -> None:
    """Check SaveVideo's hidden codec slot and the codec nested inside its auto format."""
    control = mapping_value(codec)
    options = [mapping_value(item) for item in cast("list[Json]", control.get("options", []))]
    inputs = mapping_value(mapping_value(choice).get("inputs", {}))
    required = mapping_value(inputs.get("required", {}))
    nested = cast("list[Json]", required.get("codec") or [])
    nested_codec = mapping_value(nested[1]) if len(nested) > 1 else {}
    children = [mapping_value(item) for item in cast("list[Json]", nested_codec.get("options", []))]
    checks = (
        control.get("type") == "COMFY_DYNAMICCOMBO_V3"
        and control.get("optional") is True
        and control.get("hidden") is True,
        bool(options)
        and options[0].get("key") == "auto"
        and not any(mapping_value(options[0].get("inputs", {})).values()),
        set(required) == {"codec"} and not inputs.get("optional"),
        bool(nested) and nested[0] == "COMFY_DYNAMICCOMBO_V3",
        bool(children)
        and children[0].get("key") == "auto"
        and not any(mapping_value(children[0].get("inputs", {})).values()),
    )
    if not all(checks):
        msg = "Inspect the changed native video codec controls."
        raise ValueError(msg)
