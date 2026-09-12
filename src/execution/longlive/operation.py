"""Prepare LongLive shots before starting video generation."""

import json
from typing import ClassVar
from ...models import MODELS
from ...language import translate
from ..transport import Transport
from ..events import SessionEvents
from ...state.settings import Settings
from ..inputs import VideoInputOperation
from .storyboard import parse_storyboard
from ...state.session import RecordingWindow
from ...errors import ErrorCode, ConnectorError
from ...state.generation.longlive import LongLiveRequest


class LongLiveOperation(VideoInputOperation[LongLiveRequest]):
    """Stage an opening shot and later transitions before generation."""

    connection_name: ClassVar[str] = MODELS["longlive-v2"].connection_name

    def validate(self, settings: Settings) -> None:
        """Check capture inputs and shot order; reject unsupported image input."""
        super().validate(settings)
        if self.inputs.image is not None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.longliveImagesUnsupported"))
        parse_storyboard(json.dumps([shot.to_dict() for shot in self.inputs.shots]))

    async def begin_generation(
        self, transport: Transport, events: SessionEvents, max_capture_seconds: float
    ) -> RecordingWindow:
        """Schedule the opening shot and later transitions, then start generation."""
        del transport, max_capture_seconds
        inputs = self.inputs
        await events.command_reply("set_seed", {"seed": inputs.seed})
        await events.command_reply("set_shot", {"prompt": inputs.prompt})
        for shot in inputs.shots:
            command = "schedule_shot" if shot.transition == "soft" else "schedule_scene_cut"
            await events.command_reply(command, {"prompt": shot.prompt, "at_session_chunk": shot.at_session_chunk})
        await events.command_reply("start", {})
        return RecordingWindow(0, inputs.duration_seconds)


__all__ = ["LongLiveOperation"]
