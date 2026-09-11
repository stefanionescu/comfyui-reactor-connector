"""Prepare a portrait and speech script for one LTX recording."""

import json
from typing import ClassVar
from ...language import translate
from ..operation import RecordingWindow
from ..transport import Transport
from dataclasses import dataclass
from ..events import SessionEvents
from ...settings.settings import Settings
from ...errors import ErrorCode, ConnectorError
from ....config.models.identities import MODELS
from ..inputs import VideoInputs, validate_capture_inputs
from ....config.generation.speech import (
    MIN_SPEECH_SECONDS,
    MAX_SCENE_CHARACTERS,
    MAX_WORDS_PER_MINUTE,
    MIN_WORDS_PER_MINUTE,
    MAX_SCRIPT_CHARACTERS,
    RECORDING_TAIL_SECONDS,
    DEFAULT_WORDS_PER_MINUTE,
)


@dataclass(frozen=True, slots=True)
class LtxSpeakRequest(VideoInputs):
    """Keep take conditions fixed until the session owner ends the run."""

    script: str = ""
    words_per_minute: int = DEFAULT_WORDS_PER_MINUTE
    model_name: ClassVar[str] = MODELS["ltx2"].connection_name
    requires_audio: ClassVar[bool] = True

    def validate(self, settings: Settings) -> None:
        """Check the portrait, script, speech pace, and LTX recording limits."""
        validate_capture_inputs(self.duration_seconds, self.seed, settings)
        if self.duration_seconds < MIN_SPEECH_SECONDS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.ltxDuration"))
        if type(self.prompt) is not str or len(self.prompt) > MAX_SCENE_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.ltxSceneLength"))
        if type(self.script) is not str or not self.script.strip() or len(self.script) > MAX_SCRIPT_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.speechLength"))
        if (
            type(self.words_per_minute) is not int
            or not MIN_WORDS_PER_MINUTE <= self.words_per_minute <= MAX_WORDS_PER_MINUTE
        ):
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.speechPace"))
        if (
            type(self.image) is not bytes
            or not self.image
            or len(self.image) > settings.max_upload_megabytes * 1_048_576
        ):
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.portraitUploadLimit"))

    async def configure(
        self, transport: Transport, events: SessionEvents, max_capture_seconds: float
    ) -> RecordingWindow:
        """Upload the portrait and script, validate the offered speech pace, and start speech."""
        del max_capture_seconds
        audio = [
            track
            for track in transport.tracks
            if track.name == "main_audio" and track.kind == "audio" and track.direction == "recvonly"
        ]
        if len(audio) != 1:
            raise ConnectorError(ErrorCode.UNAVAILABLE, translate("main", "errors.ltxAudioMissing"))
        if self.image is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.portraitRequired"))
        reference = await events.call(
            "upload", transport.upload_file(self.image, name="input.png", mime_type="image/png")
        )
        await events.command_reply("set_avatar_image", {"avatar_image": reference})
        await events.command_reply("set_script", {"script": self.script})
        state = await events.call("speech_state", events.snapshot("state_update"))
        minimum, maximum = state.get("wpm_min"), state.get("wpm_max")
        if (
            not isinstance(minimum, (int, float))
            or isinstance(minimum, bool)
            or not isinstance(maximum, (int, float))
            or isinstance(maximum, bool)
            or not 0 < minimum <= maximum <= MAX_WORDS_PER_MINUTE
            or minimum != int(minimum)
            or maximum != int(maximum)
        ):
            raise ConnectorError(
                ErrorCode.UNAVAILABLE,
                translate("main", "errors.speechPaceMissing"),
                diagnostic_detail=json.dumps(
                    {
                        "state_keys": sorted(state)[:40],
                        "minimum_type": type(minimum).__name__,
                        "maximum_type": type(maximum).__name__,
                        "message_types": sorted(events.message_types),
                    }
                ),
            )
        minimum, maximum = int(minimum), int(maximum)
        if not minimum <= self.words_per_minute <= maximum:
            raise ConnectorError(
                ErrorCode.INVALID_INPUT, translate("main", "errors.speechPaceRange", minimum=minimum, maximum=maximum)
            )
        await events.command_reply("set_wpm", {"wpm": self.words_per_minute})
        # Recording fragments need later media to close after the requested capture ends.
        await events.command_reply(
            "set_duration_seconds",
            {"duration_seconds": self.duration_seconds + RECORDING_TAIL_SECONDS},
        )
        await events.command_reply("set_seed", {"seed": self.seed})
        if self.prompt.strip():
            await events.command_reply("set_prompt", {"prompt": self.prompt})
        await events.command_reply("start", {})
        return RecordingWindow(0, self.duration_seconds)
