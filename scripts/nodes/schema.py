"""Export registered node schemas without starting ComfyUI or executing nodes."""

import sys
import json
from typing import get_args, get_type_hints
import inspect

from comfy_api.latest import io
from comfy_extras.nodes_audio import SaveAudioAdvanced
from comfy_extras.nodes_video import LoadVideo, SaveVideo

from .native import image_schema, describe_schemas
from ...src.extension import NODE_REGISTRATIONS
from ...src.nodes.base import VideoNode

CATEGORIES = {f'Reactor/{group}' for group in ('Generate', 'Edit', 'Live', 'Worlds', 'Plans')}


def read_input_names(node: type[io.ComfyNode]) -> set[str]:
    """Read the names that the entry point of a node receives; video nodes take the run number through their base.

    A generate that takes `**inputs: Unpack[<TypedDict>]` receives the keys of that TypedDict.
    """
    if not issubclass(node, VideoNode):
        return set(inspect.signature(node.execute).parameters)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType] # reason: The host base class leaves execute untyped; the check reads only its signature.
    names = {'variation'}
    hints = get_type_hints(node.generate)
    for parameter in inspect.signature(node.generate).parameters.values():
        if parameter.kind is inspect.Parameter.VAR_KEYWORD:
            (inputs,) = get_args(hints[parameter.name])
            names.update(inputs.__required_keys__ | inputs.__optional_keys__)
        else:
            names.add(parameter.name)
    return names


def main() -> None:
    """Describe the real node inputs and reject incomplete or conflicting registrations."""
    schemas: dict[str, io.Schema] = {}
    for node in NODE_REGISTRATIONS:
        schema = node.define_schema()
        if schema.node_id in schemas:
            msg = 'Each node must have a unique ID.'
            raise ValueError(msg)
        parameters = read_input_names(node)
        if parameters != {item.id for item in schema.inputs}:
            msg = f'Align the schema and execution inputs for {schema.node_id}.'
            raise ValueError(msg)
        if not schema.display_name or not schema.description or schema.category not in CATEGORIES:
            msg = f'Declare a display name, description, and Reactor category for {schema.node_id}.'
            raise ValueError(msg)
        schemas[schema.node_id] = schema
    # The host nodes that the generated examples connect to.
    native = describe_schemas([LoadVideo.define_schema(), SaveVideo.define_schema(), SaveAudioAdvanced.define_schema()])
    native['LoadImage'] = image_schema()
    exported = {'reactor': describe_schemas(list(schemas.values())), 'native': native}
    sys.stdout.write(json.dumps(exported, indent=2) + '\n')


if __name__ == '__main__':
    main()
