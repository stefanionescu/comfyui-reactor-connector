"""Prepare Helios prompt changes before starting generation."""

import json
from ...language import translate
from ...errors import ErrorCode, ConnectorError
from ...serialization import parse_json, mapping_value
from ...state.generation.helios import ScheduledPrompt
from ....config.generation.session import MAX_PROMPT_CHARACTERS
from ....config.generation.prompts import MAX_PROMPTS, MAX_PROMPT_CHUNK, MAX_SEQUENCE_BYTES


def validate_prompt(prompt: ScheduledPrompt) -> None:
    """Require a nonempty prompt and a supported later chunk number."""
    if type(prompt.chunk) is not int or not 1 <= prompt.chunk <= MAX_PROMPT_CHUNK:
        raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.promptChunk"))
    if type(prompt.prompt) is not str or not prompt.prompt.strip() or len(prompt.prompt) > MAX_PROMPT_CHARACTERS:
        raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.laterPromptLength"))


def parse_sequence(value: str) -> tuple[ScheduledPrompt, ...]:
    """Reject ambiguous schedules and fields that are not prompt inputs."""
    if type(value) is not str or len(value.encode()) > MAX_SEQUENCE_BYTES:
        raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.promptSequenceSize"))
    invalid = ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.promptSequenceOrder"))
    payload = parse_json(value, max_bytes=MAX_SEQUENCE_BYTES, max_depth=4)
    if not isinstance(payload, list) or len(payload) > MAX_PROMPTS:
        raise invalid
    prompts: list[ScheduledPrompt] = []
    for item in payload:
        fields = mapping_value(item)
        if set(fields) != {"chunk", "prompt"}:
            raise invalid
        chunk, prompt = fields["chunk"], fields["prompt"]
        if type(chunk) is not int or type(prompt) is not str:
            raise invalid
        scheduled = ScheduledPrompt(chunk, prompt)
        validate_prompt(scheduled)
        if prompts and scheduled.chunk <= prompts[-1].chunk:
            raise invalid
        prompts.append(scheduled)
    return tuple(prompts)


def append_prompt(previous: str, prompt: ScheduledPrompt) -> str:
    """Append one prompt and validate the complete serialized sequence."""
    validate_prompt(prompt)
    encoded = json.dumps([item.to_dict() for item in (*parse_sequence(previous), prompt)])
    parse_sequence(encoded)
    return encoded


__all__ = ["append_prompt", "parse_sequence", "validate_prompt"]
