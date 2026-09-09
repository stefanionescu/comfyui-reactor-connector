"""Choose only a SANA input path confirmed by the connected deployment."""

from ...language import translate
from ..transport import Transport
from ...errors import ErrorCode, ConnectorError
from ...serialization import mapping_value, validate_json


def source_mode(schema: object, transport: Transport) -> str:
    """Support the documented file API and the observed camera-only deployment."""
    document = mapping_value(validate_json(schema))
    paths = mapping_value(document.get("paths"))
    commands = set[str]()
    for path, raw in paths.items():
        entry = mapping_value(raw)
        post = mapping_value(entry.get("post"))
        name = post.get("operationId")
        if isinstance(name, str) and path == f"/events/{name}":
            commands.add(name)
    required = {"start", "set_prompt", "set_seed", "set_anchor_interval"}
    if required.issubset(commands):
        if {"set_video", "set_mode"}.issubset(commands):
            return "file"
        if not {"set_video", "set_mode"}.intersection(commands) and any(
            track.name == "camera" and track.kind == "video" and track.direction == "sendonly"
            for track in transport.tracks
        ):
            return "camera"
    raise ConnectorError(
        ErrorCode.UNAVAILABLE,
        translate("main", "errors.sanaUnsupported"),
    )
