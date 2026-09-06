"""Validate LongLive storyboards before allocating a remote session."""

import json
from dataclasses import dataclass
from typing import ClassVar

from ..config import Settings
from ..errors import ConnectorError, ErrorCode
from ..json_data import object_value, parse_json
from .events import SessionEvents
from .inputs import VideoInputs
from .transport import Transport

MAX_SHOTS = 32
MAX_STORYBOARD_BYTES = 128_000


@dataclass(frozen=True, slots=True)
class Shot:
    """A prompt change scheduled on the provider's cumulative chunk clock."""

    at_session_chunk: int
    transition: str
    prompt: str

    def validate(self) -> None:
        if type(self.at_session_chunk) is not int or not 1 <= self.at_session_chunk <= 100_000:
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Place a later shot at chunk 1 or above.")
        if self.transition not in ("soft", "cut"):
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Choose a soft transition or a cut.")
        if type(self.prompt) is not str or not self.prompt.strip() or len(self.prompt) > 20_000:
            raise ConnectorError(
                ErrorCode.INVALID_INPUT, "Enter a shot prompt of 1 to 20,000 characters."
            )

    def to_dict(self) -> dict[str, object]:
        return {
            "at_session_chunk": self.at_session_chunk,
            "transition": self.transition,
            "prompt": self.prompt,
        }


def parse_storyboard(value: str) -> tuple[Shot, ...]:
    """Reject ambiguous ordering and unknown fields rather than execute raw commands."""
    if type(value) is not str or len(value.encode()) > MAX_STORYBOARD_BYTES:
        raise ConnectorError(ErrorCode.INVALID_INPUT, "Keep the storyboard within 128 KB.")
    try:
        data = parse_json(value, max_bytes=MAX_STORYBOARD_BYTES, max_depth=4)
        if not isinstance(data, list) or len(data) > MAX_SHOTS:
            raise ValueError
        shots: list[Shot] = []
        for item in data:
            fields = object_value(item)
            if set(fields) != {"at_session_chunk", "transition", "prompt"}:
                raise ValueError
            chunk, transition, prompt = (
                fields["at_session_chunk"],
                fields["transition"],
                fields["prompt"],
            )
            if type(chunk) is not int or type(transition) is not str or type(prompt) is not str:
                raise ValueError
            shot = Shot(chunk, transition, prompt)
            shot.validate()
            if shots and shot.at_session_chunk <= shots[-1].at_session_chunk:
                raise ValueError
            shots.append(shot)
        return tuple(shots)
    except (ValueError, TypeError, RecursionError):
        raise ConnectorError(
            ErrorCode.INVALID_INPUT,
            "Use a storyboard of at most 32 shots with distinct, increasing chunk numbers.",
        ) from None


def append_shot(previous: str, shot: Shot) -> str:
    shot.validate()
    encoded = json.dumps([item.to_dict() for item in (*parse_storyboard(previous), shot)])
    parse_storyboard(encoded)
    return encoded


@dataclass(frozen=True, slots=True)
class LongLiveRequest(VideoInputs):
    """Stage a complete shot sequence before starting the shared video capture."""

    shots: tuple[Shot, ...] = ()
    model_name: ClassVar[str] = "reactor/longlive-v2"

    def validate(self, settings: Settings) -> None:
        VideoInputs.validate(self, settings)
        if self.image is not None:
            raise ConnectorError(
                ErrorCode.INVALID_INPUT, "LongLive accepts shot prompts, not images."
            )
        parse_storyboard(json.dumps([shot.to_dict() for shot in self.shots]))

    async def configure(self, transport: Transport, events: SessionEvents) -> None:
        await events.command("set_seed", {"seed": self.seed})
        await events.command("set_shot", {"prompt": self.prompt})
        for shot in self.shots:
            command = "schedule_shot" if shot.transition == "soft" else "schedule_scene_cut"
            await events.command(
                command, {"prompt": shot.prompt, "at_session_chunk": shot.at_session_chunk}
            )
        await events.command("start", {})
