"""Prepare Helios prompt changes before starting generation."""

import json
from dataclasses import dataclass

from ..errors import ConnectorError, ErrorCode
from ..json_data import object_value, parse_json

MAX_PROMPTS = 32
MAX_SEQUENCE_BYTES = 128_000


@dataclass(frozen=True, slots=True)
class ScheduledPrompt:
    """A later prompt on Helios's chunk clock."""

    chunk: int
    prompt: str

    def validate(self) -> None:
        if type(self.chunk) is not int or not 1 <= self.chunk <= 100_000:
            raise ConnectorError(
                ErrorCode.INVALID_INPUT, "Choose a later prompt's chunk from 1 to 100,000."
            )
        if type(self.prompt) is not str or not self.prompt.strip() or len(self.prompt) > 20_000:
            raise ConnectorError(
                ErrorCode.INVALID_INPUT, "Enter a later prompt of 1 to 20,000 characters."
            )

    def to_dict(self) -> dict[str, object]:
        return {"chunk": self.chunk, "prompt": self.prompt}


def parse_sequence(value: str) -> tuple[ScheduledPrompt, ...]:
    """Reject ambiguous schedules and fields that are not prompt inputs."""
    if type(value) is not str or len(value.encode()) > MAX_SEQUENCE_BYTES:
        raise ConnectorError(ErrorCode.INVALID_INPUT, "Keep the prompt sequence within 128 KB.")
    try:
        data = parse_json(value, max_bytes=MAX_SEQUENCE_BYTES, max_depth=4)
        if not isinstance(data, list) or len(data) > MAX_PROMPTS:
            raise ValueError
        prompts: list[ScheduledPrompt] = []
        for item in data:
            fields = object_value(item)
            if set(fields) != {"chunk", "prompt"}:
                raise ValueError
            chunk, prompt = fields["chunk"], fields["prompt"]
            if type(chunk) is not int or type(prompt) is not str:
                raise ValueError
            scheduled = ScheduledPrompt(chunk, prompt)
            scheduled.validate()
            if prompts and scheduled.chunk <= prompts[-1].chunk:
                raise ValueError
            prompts.append(scheduled)
        return tuple(prompts)
    except (ValueError, TypeError, RecursionError):
        raise ConnectorError(
            ErrorCode.INVALID_INPUT,
            "Use at most 32 later prompts with distinct, increasing chunk numbers.",
        ) from None


def append_prompt(previous: str, prompt: ScheduledPrompt) -> str:
    prompt.validate()
    encoded = json.dumps([item.to_dict() for item in (*parse_sequence(previous), prompt)])
    parse_sequence(encoded)
    return encoded
