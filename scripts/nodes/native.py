"""Describe installed host node contracts used by the generated examples."""

from typing import cast
from nodes import LoadImage
from comfy_api.latest import io
from comfy_extras.nodes_audio import SaveAudioAdvanced
from comfy_extras.nodes_video import LoadVideo, SaveVideo


def describe_schema(schema: io.Schema) -> dict[str, object]:
    """Describe one node schema's public metadata, inputs, and outputs."""
    return {
        "display_name": schema.display_name,
        "description": schema.description,
        "category": schema.category,
        "search_aliases": schema.search_aliases,
        "inputs": [
            {
                "name": item.id,
                "type": item.io_type,
                "widget": isinstance(item, (io.WidgetInput, io.DynamicCombo.Input)),
                **item.as_dict(),
                **({"options": []} if schema.node_id == "LoadVideo" and item.id == "file" else {}),
            }
            for item in schema.inputs
        ],
        "outputs": [{"type": item.io_type, **item.as_dict()} for item in schema.outputs],
    }


def image_schema() -> dict[str, object]:
    """Describe LoadImage's public upload contract without exposing local file names."""
    types = cast("dict[str, dict[str, tuple[object, dict[str, object]]]]", LoadImage.INPUT_TYPES())
    files, attributes = types["required"]["image"]
    if not isinstance(files, list) or attributes.get("image_upload") is not True:
        msg = "Inspect the changed LoadImage upload input."
        raise ValueError(msg)
    return {
        "inputs": [{"name": "image", "type": "COMBO", "widget": True, "options": [], "image_upload": True}],
        "outputs": [{"type": kind} for kind in LoadImage.RETURN_TYPES],
    }


def native_schemas() -> dict[str, dict[str, object]]:
    """Describe the installed host nodes the generated examples connect to."""
    return {
        "LoadVideo": describe_schema(LoadVideo.define_schema()),
        "SaveVideo": describe_schema(SaveVideo.define_schema()),
        "SaveAudioAdvanced": describe_schema(SaveAudioAdvanced.define_schema()),
        "LoadImage": image_schema(),
    }
