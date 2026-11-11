"""Bound JSON before it enters connector contracts."""

import json
import math
from typing import cast

from .errors import ErrorCode, ConnectorError
from .config.security import MAX_JSON_BYTES, MAX_JSON_DEPTH
from .config.messages.requests import JSON_SIZE, JSON_DEPTH, JSON_SYNTAX, JSON_VALUES, JSON_MAPPING, JSON_DUPLICATE_KEY

type Json = bool | int | float | str | list[Json] | dict[str, Json] | None


def parse_json(text: str, *, max_bytes: int = MAX_JSON_BYTES, max_depth: int = MAX_JSON_DEPTH) -> Json:
    """Reject oversized, nested, duplicate-key, and non-finite JSON input.

    Args:
        text: The JSON text to parse.
        max_bytes: The largest encoded text to accept, in bytes.
        max_depth: The deepest nesting to accept.

    Returns:
        The parsed JSON value.

    Raises:
        ConnectorError: When the text is too large or is not valid JSON.

    """
    if len(text.encode('utf-8')) > max_bytes:
        raise ConnectorError(ErrorCode.INVALID_INPUT, JSON_SIZE)
    try:
        value = cast('object', json.loads(text, object_pairs_hook=_unique_fields))
        return validate_json(value, max_depth=max_depth)
    except (ValueError, RecursionError) as error:
        raise ConnectorError(ErrorCode.INVALID_INPUT, JSON_SYNTAX) from error


def _unique_fields(pairs: list[tuple[str, Json]]) -> dict[str, Json]:
    """Build a JSON object while rejecting duplicate keys.

    Args:
        pairs: The keys and values of one JSON object, in source order.

    Returns:
        The JSON object.

    Raises:
        ValueError: When a key appears twice.

    """
    result: dict[str, Json] = {}
    for key, value in pairs:
        if key in result:
            message = JSON_DUPLICATE_KEY
            raise ValueError(message)
        result[key] = value
    return result


def validate_json(value: object, *, max_depth: int = MAX_JSON_DEPTH) -> Json:
    """Copy JSON values within the nesting limit; reject other Python objects.

    Args:
        value: The Python object to check.
        max_depth: The deepest nesting that remains allowed.

    Returns:
        The copied JSON value.

    Raises:
        ConnectorError: When the value is nested too deep or is not JSON.

    """
    if max_depth < 0:
        raise ConnectorError(ErrorCode.INVALID_INPUT, JSON_DEPTH)
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    if isinstance(value, list):
        items = cast('list[object]', value)
        return [validate_json(item, max_depth=max_depth - 1) for item in items]
    if isinstance(value, dict):
        entries = cast('dict[object, object]', value)
        if all(isinstance(key, str) for key in entries):
            return {cast('str', key): validate_json(item, max_depth=max_depth - 1) for key, item in entries.items()}
    raise ConnectorError(ErrorCode.INVALID_INPUT, JSON_VALUES)


def mapping_value(value: Json) -> dict[str, Json]:
    """Require an object at a public JSON boundary.

    Args:
        value: The JSON value to check.

    Returns:
        The same value, as an object.

    Raises:
        ConnectorError: When the value is not an object.

    """
    if not isinstance(value, dict):
        raise ConnectorError(ErrorCode.INVALID_INPUT, JSON_MAPPING)
    return value
