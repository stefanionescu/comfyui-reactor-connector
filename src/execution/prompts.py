"""Prepare Helios prompt changes before starting generation."""

import json
from ..codes import ErrorCode
from dataclasses import dataclass
from ..errors import ConnectorError
from ..serialization import parse_json, mapping_value
from ...config.generation.session import MAX_PROMPT_CHARACTERS
from ...config.generation.prompts import MAX_PROMPTS, MAX_PROMPT_CHUNK, MAX_SEQUENCE_BYTES


@dataclass(frozen=True, slots=True)
class ScheduledPrompt:
    """A later prompt on Helios's chunk clock."""

    chunk: int
    prompt: str

    def validate(self) -> None:
        """Require a nonempty prompt and a supported later chunk number."""
        if type(self.chunk) is not int or not 1 <= self.chunk <= MAX_PROMPT_CHUNK:
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Choose a later prompt's chunk from 1 to 100,000.")
        if type(self.prompt) is not str or not self.prompt.strip() or len(self.prompt) > MAX_PROMPT_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Enter a later prompt of 1 to 20,000 characters.")

    def to_dict(self) -> dict[str, object]:
        """Encode the scheduled prompt using Reactor command field names."""
        return {"chunk": self.chunk, "prompt": self.prompt}


def parse_sequence(value: str) -> tuple[ScheduledPrompt, ...]:
    """Reject ambiguous schedules and fields that are not prompt inputs."""
    if type(value) is not str or len(value.encode()) > MAX_SEQUENCE_BYTES:
        raise ConnectorError(ErrorCode.INVALID_INPUT, "Keep the prompt sequence within 128 KB.")
    invalid = ConnectorError(
        ErrorCode.INVALID_INPUT, "Use at most 32 later prompts with distinct, increasing chunk numbers."
    )
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
        scheduled.validate()
        if prompts and scheduled.chunk <= prompts[-1].chunk:
            raise invalid
        prompts.append(scheduled)
    return tuple(prompts)


def append_prompt(previous: str, prompt: ScheduledPrompt) -> str:
    """Append one prompt and validate the complete serialized sequence."""
    prompt.validate()
    encoded = json.dumps([item.to_dict() for item in (*parse_sequence(previous), prompt)])
    parse_sequence(encoded)
    return encoded
