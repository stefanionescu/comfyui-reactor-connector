"""Validate named example inputs and serialize them in ComfyUI schema order."""

import math
from typing import cast
from pathlib import Path
from collections.abc import Mapping

from ...src.serialization import Json, mapping_value


def build_node(node_id: int, kind: str, widgets: list[Json], *, title: str | None = None) -> dict[str, Json]:
    """Create a serialized ComfyUI node with stable widget order and an optional display title.

    Args:
        node_id: The ID of the node, which also sets its order.
        kind: The node type that ComfyUI registers.
        widgets: The widget values, in schema order.
        title: The title to show, or None to show the default one.

    Returns:
        The serialized node.

    """
    value: dict[str, Json] = {
        'id': node_id,
        'type': kind,
        'pos': [0, 0],
        'size': [0, 0],
        'flags': {},
        'order': node_id,
        'mode': 0,
        'inputs': [],
        'outputs': [],
        'properties': {'Node name for S&R': kind},
        'widgets_values': widgets,
    }
    if title:
        value['title'] = f'{title} (Reactor)' if kind.startswith('ReactorInc') else title
    return value


def build_input(name: str, kind: str, link: int, *, has_widget: bool = False) -> dict[str, Json]:
    """Describe a connected input and its optional widget binding.

    Args:
        name: The name of the input socket.
        kind: The type of the input socket.
        link: The ID of the link that feeds the input.
        has_widget: Whether the input also binds a widget of the same name.

    Returns:
        The serialized input.

    """
    value: dict[str, Json] = {'name': name, 'type': kind, 'link': link}
    if has_widget:
        value['widget'] = {'name': name}
    return value


def widget_values(schema: Json, values: Mapping[str, str | float | bool]) -> list[Json]:
    """Reject missing or unknown widget names before converting values to saved positions.

    Args:
        schema: The exported schema of the node.
        values: The widget values of the example, by input name.

    Returns:
        The widget values, in the order that ComfyUI saves them.

    Raises:
        ValueError: When the names differ from the schema, or a value is not valid.

    """
    inputs = cast('list[dict[str, Json]]', mapping_value(schema)['inputs'])
    widgets = [item for item in inputs if item['widget']]
    expected = {str(item['name']) for item in widgets}
    if any(item.get('control_after_generate') for item in widgets):
        expected.add('control_after_generate')
    if set(values) != expected:
        message = (
            f'Match widget names to the schema. Missing: {expected - values.keys()}; extra: {values.keys() - expected}.'
        )
        raise ValueError(message)
    result: list[Json] = []
    for item in widgets:
        value = values[str(item['name'])]
        validate_value(item, value=value)
        result.append(float(value) if item['type'] == 'FLOAT' else value)
        if item.get('control_after_generate'):
            behavior = values['control_after_generate']
            if behavior not in {'fixed', 'increment', 'decrement', 'randomize'}:
                message = 'Choose a supported seed behavior for the workflow.'
                raise ValueError(message)
            result.append(behavior)
    return result


def validate_value(item: dict[str, Json], *, value: str | float | bool) -> None:
    """Check widget types, choices, and numeric limits against the registered schema.

    Args:
        item: The exported schema of one widget input.
        value: The value that the example gives the widget.

    Raises:
        ValueError: When the value has the wrong type or is outside its limits.

    """
    kind = item['type']
    valid_type = {
        'STRING': isinstance(value, str),
        'BOOLEAN': isinstance(value, bool),
        'INT': type(value) is int,
        'FLOAT': type(value) in {int, float},
        'COMBO': value in cast('list[Json]', item.get('options', [])),
    }.get(str(kind), False)
    if not valid_type:
        message = f'Use a valid {kind} value for {item["name"]} in the workflow.'
        raise ValueError(message)
    if kind in {'INT', 'FLOAT'}:
        number = float(value)
        lower = float(cast('float', item.get('min', -math.inf)))
        upper = float(cast('float', item.get('max', math.inf)))
        if not math.isfinite(number) or not lower <= number <= upper:
            message = f"Keep {item['name']} within its node's numeric limits."
            raise ValueError(message)


def validate_sources(schema: Json, sources: tuple[str, ...]) -> None:
    """Require every mandatory media connection and reject unknown source sockets.

    Args:
        schema: The exported schema of the node.
        sources: The names of the media inputs that the example connects.

    Raises:
        ValueError: When a required source is missing or a source is unknown.

    """
    inputs = cast('list[dict[str, Json]]', mapping_value(schema)['inputs'])
    media = {str(item['name']): item for item in inputs if not item['widget']}
    required = {name for name, item in media.items() if not item.get('optional')}
    if set(sources) - media.keys() or required - set(sources):
        message = "Match the workflow's media sources to the required node sockets."
        raise ValueError(message)


def validate_node_sockets(nodes: list[Json], schemas: dict[str, Json]) -> None:
    """Reject connected input names or socket types that disagree with a registered node.

    Args:
        nodes: The serialized workflow nodes.
        schemas: The exported schemas, by node type.

    Raises:
        ValueError: When an input or output of a node disagrees with its schema.

    """
    for value in nodes:
        node = mapping_value(value)
        kind = str(node['type'])
        if kind not in schemas:
            continue
        schema = mapping_value(schemas[kind])
        inputs = {str(item['name']): item['type'] for item in cast('list[dict[str, Json]]', schema['inputs'])}
        connected = cast('list[dict[str, Json]]', node['inputs'])
        if any(inputs.get(str(item['name'])) != item['type'] for item in connected):
            message = f'Match connected input names and types to {kind}.'
            raise ValueError(message)
        expected = [item['type'] for item in cast('list[dict[str, Json]]', schema['outputs'])]
        saved = [item['type'] for item in cast('list[dict[str, Json]]', node['outputs'])]
        if saved != expected:
            message = f'Match saved output sockets to {kind}.'
            raise ValueError(message)


def output_types(schema: Json) -> list[str]:
    """Read socket types from a registered node schema.

    Args:
        schema: The exported schema of the node.

    Returns:
        The type of each output socket, in order.

    Raises:
        TypeError: When the outputs are not a list.

    """
    outputs = mapping_value(schema)['outputs']
    if not isinstance(outputs, list):
        message = 'Node outputs must be a list.'
        raise TypeError(message)
    return [str(mapping_value(item)['type']) for item in outputs]


def native_widget_values(kind: str, schema: Json, filename_prefix: str = '') -> list[Json]:
    """Check the four native node contracts used by these examples before serialization.

    Args:
        kind: The type of the host node.
        schema: The exported schema of the host node.
        filename_prefix: The path prefix under which a save node writes its file.

    Returns:
        The widget values of the host node, in saved order.

    Raises:
        ValueError: When the inputs of the host node have changed.

    """
    inputs = [mapping_value(item) for item in cast('list[Json]', mapping_value(schema)['inputs'])]
    expected = {
        'LoadImage': ['image'],
        'LoadVideo': ['file'],
        'SaveVideo': ['video', 'filename_prefix', 'format', 'codec'],
        'SaveAudioAdvanced': ['audio', 'filename_prefix', 'format'],
    }
    if [item['name'] for item in inputs] != expected[kind]:
        message = f'Inspect the changed native input order for {kind}.'
        raise ValueError(message)
    if kind in {'LoadImage', 'LoadVideo'}:
        if inputs[0]['type'] != 'COMBO':
            message = f'Inspect the changed upload input for {kind}.'
            raise ValueError(message)
        return ['', 'image']
    selected = 'auto' if kind == 'SaveVideo' else 'flac'
    options = cast('list[Json]', inputs[2]['options'])
    choice = mapping_value(options[0])
    if inputs[2]['type'] != 'COMFY_DYNAMICCOMBO_V3' or choice['key'] != selected:
        message = f'Inspect the changed native format selection for {kind}.'
        raise ValueError(message)
    if kind == 'SaveAudioAdvanced':
        if any(mapping_value(choice['inputs']).values()):
            message = 'Inspect the changed FLAC widget controls.'
            raise ValueError(message)
        return [filename_prefix, 'flac']
    validate_video_codec(inputs[3], choice)
    return [filename_prefix, 'auto', 'auto', 'auto']


def validate_video_codec(codec: Json, choice: Json) -> None:
    """Check SaveVideo's hidden codec slot and the codec nested inside its auto format.

    Args:
        codec: The exported schema of the codec input.
        choice: The exported first option of the format input.

    Raises:
        ValueError: When the codec controls have changed.

    """
    control = mapping_value(codec)
    options = [mapping_value(item) for item in cast('list[Json]', control.get('options', []))]
    inputs = mapping_value(mapping_value(choice).get('inputs', {}))
    required = mapping_value(inputs.get('required', {}))
    nested = cast('list[Json]', required.get('codec') or [])
    nested_codec = mapping_value(nested[1]) if len(nested) > 1 else {}
    children = [mapping_value(item) for item in cast('list[Json]', nested_codec.get('options', []))]
    checks = (
        control.get('type') == 'COMFY_DYNAMICCOMBO_V3'
        and control.get('optional') is True
        and control.get('hidden') is True,
        bool(options)
        and options[0].get('key') == 'auto'
        and not any(mapping_value(options[0].get('inputs', {})).values()),
        set(required) == {'codec'} and not inputs.get('optional'),
        bool(nested) and nested[0] == 'COMFY_DYNAMICCOMBO_V3',
        bool(children)
        and children[0].get('key') == 'auto'
        and not any(mapping_value(children[0].get('inputs', {})).values()),
    )
    if not all(checks):
        message = 'Inspect the changed native video codec controls.'
        raise ValueError(message)


def save_workflows(generated: dict[Path, str], *, check: bool) -> list[str]:
    """Write validated workflows, or report differences without changing files.

    Args:
        generated: The text of each workflow, by destination path.
        check: Whether to compare the files without writing them.

    Returns:
        One message for each file that differs.

    """
    issues: list[str] = []
    for path, text in generated.items():
        if check:
            if not path.exists() or path.read_text(encoding='utf-8') != text:
                issues.append(f'Rebuild {path.name} with mise run comfy:workflows:build.')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8')
    return issues
