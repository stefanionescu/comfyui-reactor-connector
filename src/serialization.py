"""Bound JSON before it enters connector contracts."""

import json
import math
from typing import cast
from .language import translate
from .errors import ErrorCode, ConnectorError
from ..config.serialization import MAX_JSON_BYTES, MAX_JSON_DEPTH

type Json = bool | int | float | str | list[Json] | dict[str, Json] | None


def parse_json(text: str, *, max_bytes: int = MAX_JSON_BYTES, max_depth: int = MAX_JSON_DEPTH) -> Json:
    """Reject oversized, nested, duplicate-key, and non-finite JSON input."""
    if len(text.encode("utf-8")) > max_bytes:
        raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.jsonSize"))
    try:
        value = cast("object", json.loads(text, object_pairs_hook=_unique_fields))
        return validate_json(value, max_depth=max_depth)
    except (ValueError, RecursionError) as error:
        raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.jsonSyntax")) from error


def _unique_fields(pairs: list[tuple[str, Json]]) -> dict[str, Json]:
    """Build a JSON object while rejecting duplicate keys."""
    result: dict[str, Json] = {}
    for key, value in pairs:
        if key in result:
            msg = translate("main", "errors.jsonDuplicateKey")
            raise ValueError(msg)
        result[key] = value
    return result


def validate_json(value: object, *, max_depth: int = MAX_JSON_DEPTH) -> Json:
    """Copy JSON data within size and nesting limits; reject other Python objects."""
    if max_depth < 0:
        raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.jsonDepth"))
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    if isinstance(value, list):
        items = cast("list[object]", value)
        return [validate_json(item, max_depth=max_depth - 1) for item in items]
    if isinstance(value, dict):
        entries = cast("dict[object, object]", value)
        if all(isinstance(key, str) for key in entries):
            return {cast("str", key): validate_json(item, max_depth=max_depth - 1) for key, item in entries.items()}
    raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.jsonValues"))


def mapping_value(value: Json) -> dict[str, Json]:
    """Require an object at a public JSON boundary."""
    if not isinstance(value, dict):
        raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.jsonObject"))
    return value
