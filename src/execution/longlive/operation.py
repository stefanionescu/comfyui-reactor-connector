"""Prepare LongLive shots before starting video generation."""

import json
from typing import ClassVar, override
from dataclasses import asdict

from ..events import SessionEvents
from ..inputs import VideoInputOperation
from ...errors import ErrorCode, ConnectorError
from ...models import MODELS
from ..transport import SessionTransport
from .storyboard import parse_storyboard
from ...state.session import RecordingWindow
from ...state.settings import Settings
from ...config.messages.inputs import LONGLIVE_IMAGES_UNSUPPORTED
from ...state.generation.longlive import LongLiveRequest


class LongLiveOperation(VideoInputOperation[LongLiveRequest]):
    """Stage an opening shot and later transitions before generation."""

    connection_name: ClassVar[str] = MODELS['longlive-v2'].connection_name

    @override
    def validate(self, settings: Settings) -> None:
        """Check capture inputs and shot order; reject unsupported image input."""
        super().validate(settings)
        if self.inputs.image is not None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, LONGLIVE_IMAGES_UNSUPPORTED)
        parse_storyboard(json.dumps([asdict(shot) for shot in self.inputs.shots]))

    @override
    async def begin_generation(self, transport: SessionTransport, events: SessionEvents) -> RecordingWindow:
        """Schedule the opening shot and later transitions, then start generation."""
        del transport
        inputs = self.inputs
        await events.command_reply('set_seed', {'seed': inputs.seed})
        await events.command_reply('set_shot', {'prompt': inputs.prompt})
        for shot in inputs.shots:
            command = 'schedule_shot' if shot.transition == 'soft' else 'schedule_scene_cut'
            await events.command_reply(command, {'prompt': shot.prompt, 'at_session_chunk': shot.at_session_chunk})
        await events.command_reply('start', {})
        return RecordingWindow(0, inputs.duration_seconds)
