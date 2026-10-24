"""Describe installed host node contracts used by the generated examples."""

from typing import cast

from comfy_api.latest import io

from nodes import LoadImage


def describe_schemas(schemas: list[io.Schema]) -> dict[str, dict[str, object]]:
    """Describe the public metadata, inputs, and outputs of each node schema, by node ID."""
    described: dict[str, dict[str, object]] = {}
    for schema in schemas:
        described[schema.node_id] = {
            'display_name': schema.display_name,
            'description': schema.description,
            'category': schema.category,
            'search_aliases': schema.search_aliases,
            'inputs': [
                {
                    'name': item.id,
                    'type': item.io_type,
                    'widget': isinstance(item, (io.WidgetInput, io.DynamicCombo.Input)),
                    **item.as_dict(),
                    **({'options': []} if schema.node_id == 'LoadVideo' and item.id == 'file' else {}),
                }
                for item in schema.inputs
            ],
            'outputs': [{'type': item.io_type, **item.as_dict()} for item in schema.outputs],
        }
    return described


def image_schema() -> dict[str, object]:
    """Describe LoadImage's public upload contract without exposing local file names."""
    types = cast('dict[str, dict[str, tuple[object, dict[str, object]]]]', LoadImage.INPUT_TYPES())
    files, attributes = types['required']['image']
    if not isinstance(files, list) or attributes.get('image_upload') is not True:
        msg = 'Inspect the changed LoadImage upload input.'
        raise ValueError(msg)
    return {
        'inputs': [{'name': 'image', 'type': 'COMBO', 'widget': True, 'options': [], 'image_upload': True}],
        'outputs': [{'type': kind} for kind in LoadImage.RETURN_TYPES],
    }
