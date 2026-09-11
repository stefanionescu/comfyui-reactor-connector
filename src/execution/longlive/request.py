"""Prepare LongLive shots before starting video generation."""

import json
from typing import ClassVar
from ...models import MODELS
from ..inputs import VideoInputs
from ...language import translate
from ..transport import Transport
from dataclasses import dataclass
from ..events import SessionEvents
from ...settings.schema import Settings
from ..operation import RecordingWindow
from .storyboard import Shot, parse_storyboard
from ...errors import ErrorCode, ConnectorError


@dataclass(frozen=True, slots=True)
class LongLiveRequest(VideoInputs):
    """Stage a complete shot sequence before starting the shared video capture.

    Attributes:
        shots: Ordered shots to stage before generation.

    """

    shots: tuple[Shot, ...] = ()
    connection_name: ClassVar[str] = MODELS["longlive-v2"].connection_name

    def validate(self, settings: Settings) -> None:
        """Check capture inputs and shot order; reject unsupported image input."""
        VideoInputs.validate(self, settings)
        if self.image is not None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.longliveImagesUnsupported"))
        parse_storyboard(json.dumps([shot.to_dict() for shot in self.shots]))

    async def begin_generation(
        self, transport: Transport, events: SessionEvents, max_capture_seconds: float
    ) -> RecordingWindow:
        """Schedule the opening shot and later transitions, then start generation."""
        del transport, max_capture_seconds
        await events.command_reply("set_seed", {"seed": self.seed})
        await events.command_reply("set_shot", {"prompt": self.prompt})
        for shot in self.shots:
            command = "schedule_shot" if shot.transition == "soft" else "schedule_scene_cut"
            await events.command_reply(command, {"prompt": shot.prompt, "at_session_chunk": shot.at_session_chunk})
        await events.command_reply("start", {})
        return RecordingWindow(0, self.duration_seconds)
