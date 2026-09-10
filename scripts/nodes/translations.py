"""Validate native node labels and partial language resources."""

from __future__ import annotations

from string import Formatter
from typing import TYPE_CHECKING, cast
from ...src.serialization import Json, mapping_value
from ...quality.lib.json_config import (
    require_keys,
    require_string,
    JsonConfigError,
    require_mapping,
    read_json_mapping,
    require_string_list,
)
from ...quality.config.repository.translations import (
    NODE_TEXT_FIELDS,
    NODE_GROUP_FIELDS,
    INPUT_LABEL_FIELDS,
    OUTPUT_LABEL_FIELDS,
)

if TYPE_CHECKING:
    from pathlib import Path


def parse_placeholders(text: str, location: str) -> set[tuple[str, str | None, str | None]]:
    """Read placeholders and their formatting without changing Python's format syntax."""
    fields = set[tuple[str, str | None, str | None]]()
    try:
        for _, field, specification, conversion in Formatter().parse(text):
            if field is None:
                continue
            fields.add((field, specification, conversion))
    except ValueError as exception:
        msg = f"{location}: Correct the message placeholders: {exception}"
        raise JsonConfigError(msg) from exception
    return fields


def validate_messages(value: object, location: str) -> None:
    """Require string messages, string lists, or nested message groups."""
    if isinstance(value, str):
        parse_placeholders(value, location)
    elif isinstance(value, list):
        for item in require_string_list(cast("list[object]", value), location):
            parse_placeholders(item, location)
    else:
        for key, item in require_mapping(value, location).items():
            validate_messages(item, f"{location}.{key}")


def compare_messages(value: object, english: object, location: str) -> None:
    """Allow missing translations while rejecting unknown keys, wrong types, and changed placeholders."""
    if isinstance(english, str):
        translated = require_string(value, location)
        if parse_placeholders(translated, location) != parse_placeholders(english, location):
            msg = f"{location}: Keep the English placeholders and their formatting."
            raise JsonConfigError(msg)
    elif isinstance(english, list):
        require_string_list(value, location, is_nonempty=True)
    else:
        reference = require_mapping(english, location)
        translated_group = require_mapping(value, location)
        require_keys(translated_group, required=set(), optional=set(reference), context=location)
        for key, item in translated_group.items():
            compare_messages(item, reference[key], f"{location}.{key}")


def validate_labels(labels: object, socket: dict[str, Json], location: str) -> None:
    """Check input labels against the input's declared options and text capabilities."""
    fields = require_mapping(labels, location)
    allowed = INPUT_LABEL_FIELDS.copy()
    if socket["type"] != "STRING":
        allowed.discard("placeholder")
    if "options" not in socket:
        allowed.discard("options")
    require_keys(fields, required={"name"}, optional=allowed, context=location)
    for key, value in fields.items():
        if key != "options":
            require_string(value, f"{location}.{key}")
            continue
        options = require_mapping(value, f"{location}.options")
        choices = require_string_list(socket["options"], location)
        require_keys(options, required=set(), optional=set(choices), context=location)
        for option, label in options.items():
            require_string(label, f"{location}.options.{option}")


def validate_node_labels(labels: object, schema: dict[str, Json], location: str) -> None:
    """Match each node translation to its real input and output definitions."""
    fields = require_mapping(labels, location)
    require_keys(fields, required=NODE_TEXT_FIELDS | NODE_GROUP_FIELDS, context=location)
    for field in NODE_TEXT_FIELDS:
        require_string(fields[field], f"{location}.{field}")
    require_string_list(fields["search_aliases"], location, is_nonempty=True)
    inputs = require_mapping(fields["inputs"], f"{location}.inputs")
    outputs = require_mapping(fields["outputs"], f"{location}.outputs")
    declared_inputs = schema["inputs"]
    declared_outputs = schema["outputs"]
    if not isinstance(declared_inputs, list) or not isinstance(declared_outputs, list):
        msg = f"{location}: Export node inputs and outputs as lists."
        raise JsonConfigError(msg)
    sockets = {str(mapping_value(item)["name"]): mapping_value(item) for item in declared_inputs}
    require_keys(inputs, required=set(sockets), context=f"{location}.inputs")
    require_keys(
        outputs, required={str(index) for index in range(len(declared_outputs))}, context=f"{location}.outputs"
    )
    for name, socket in sockets.items():
        validate_labels(inputs[name], socket, f"{location}.inputs.{name}")
    for index, value in outputs.items():
        output = require_mapping(value, f"{location}.outputs.{index}")
        require_keys(output, required={"name"}, optional=OUTPUT_LABEL_FIELDS, context=location)
        for field, label in output.items():
            require_string(label, f"{location}.outputs.{index}.{field}")


def read_english(root: Path, schemas: dict[str, Json]) -> dict[str, dict[str, object]]:
    """Read the reference messages after checking their types and registered node keys."""
    english: dict[str, dict[str, object]] = {}
    for path in sorted((root / "en").glob("*.json")):
        messages = read_json_mapping(path)
        validate_messages(messages, str(path))
        if path.name == "nodeDefs.json":
            require_keys(messages, required=set(schemas), context=str(path))
            for name, schema in schemas.items():
                validate_node_labels(messages[name], mapping_value(schema), f"{path}:{name}")
        english[path.name] = messages
    return english


def validate_translations(root: Path, schemas: dict[str, Json]) -> list[str]:
    """Check English node metadata and each supplied translation without requiring extra languages."""
    issues: list[str] = []
    try:
        english = read_english(root, schemas)
    except JsonConfigError as exception:
        return [str(exception)]
    for path in sorted(root.glob("*/*.json")):
        if path.parent.name == "en":
            continue
        if path.name not in english:
            issues.append(f"{path}: Use a message file defined in the English locale.")
            continue
        try:
            compare_messages(read_json_mapping(path), english[path.name], str(path))
        except JsonConfigError as exception:
            issues.append(str(exception))
    return issues
