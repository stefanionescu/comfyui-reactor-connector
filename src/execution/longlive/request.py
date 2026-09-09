"""Prepare LongLive shots before starting video generation."""

import json
from typing import ClassVar
from ..inputs import VideoInputs
from ...language import translate
from ..transport import Transport
from dataclasses import dataclass
from ..events import SessionEvents
from ...settings.settings import Settings
from .storyboard import Shot, parse_storyboard
from ...errors import ErrorCode, ConnectorError
from ....config.models.identities import IDENTITIES


@dataclass(frozen=True, slots=True)
class LongLiveRequest(VideoInputs):
    """Stage a complete shot sequence before starting the shared video capture."""

    shots: tuple[Shot, ...] = ()
    model_name: ClassVar[str] = IDENTITIES["longlive-v2"][1]

    def validate(self, settings: Settings) -> None:
        """Check capture inputs and shot order; reject unsupported image input."""
        VideoInputs.validate(self, settings)
        if self.image is not None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.longliveImagesUnsupported"))
        parse_storyboard(json.dumps([shot.to_dict() for shot in self.shots]))

    async def configure(self, transport: Transport, events: SessionEvents) -> None:
        """Schedule the opening shot and later transitions, then start generation."""
        del transport
        await events.command("set_seed", {"seed": self.seed})
        await events.command("set_shot", {"prompt": self.prompt})
        for shot in self.shots:
            command = "schedule_shot" if shot.transition == "soft" else "schedule_scene_cut"
            await events.command(command, {"prompt": shot.prompt, "at_session_chunk": shot.at_session_chunk})
        await events.command("start", {})
