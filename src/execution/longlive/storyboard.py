"""Validate LongLive storyboards before allocating a remote session."""

import json
from ...language import translate
from ...state.generation.longlive import Shot
from ...errors import ErrorCode, ConnectorError
from ...serialization import parse_json, mapping_value
from ....config.generation.session import MAX_PROMPT_CHARACTERS
from ....config.generation.prompts import OPTIONS_TRANSITION, MAX_SHOTS, MAX_SHOT_CHUNK, MAX_STORYBOARD_BYTES


def validate_shot(shot: Shot) -> None:
    """Check the later chunk, transition choice, and shot prompt."""
    if type(shot.at_session_chunk) is not int or not 1 <= shot.at_session_chunk <= MAX_SHOT_CHUNK:
        raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.shotChunk"))
    if shot.transition not in OPTIONS_TRANSITION:
        raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.shotTransition"))
    if type(shot.prompt) is not str or not shot.prompt.strip() or len(shot.prompt) > MAX_PROMPT_CHARACTERS:
        raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.shotPrompt"))


def parse_storyboard(value: str) -> tuple[Shot, ...]:
    """Reject ambiguous ordering and unknown fields rather than execute raw commands."""
    if type(value) is not str or len(value.encode()) > MAX_STORYBOARD_BYTES:
        raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.storyboardSize"))
    invalid = ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.storyboardOrder"))
    payload = parse_json(value, max_bytes=MAX_STORYBOARD_BYTES, max_depth=4)
    if not isinstance(payload, list) or len(payload) > MAX_SHOTS:
        raise invalid
    shots: list[Shot] = []
    for item in payload:
        fields = mapping_value(item)
        if set(fields) != {"at_session_chunk", "transition", "prompt"}:
            raise invalid
        chunk, transition, prompt = (
            fields["at_session_chunk"],
            fields["transition"],
            fields["prompt"],
        )
        if type(chunk) is not int or type(transition) is not str or type(prompt) is not str:
            raise invalid
        shot = Shot(chunk, transition, prompt)
        validate_shot(shot)
        if shots and shot.at_session_chunk <= shots[-1].at_session_chunk:
            raise invalid
        shots.append(shot)
    return tuple(shots)


def append_shot(previous: str, shot: Shot) -> str:
    """Append a shot and validate the complete serialized storyboard."""
    validate_shot(shot)
    encoded = json.dumps([item.to_dict() for item in (*parse_storyboard(previous), shot)])
    parse_storyboard(encoded)
    return encoded


__all__ = ["append_shot", "parse_storyboard", "validate_shot"]
