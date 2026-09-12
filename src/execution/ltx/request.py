"""Prepare a portrait and speech script for one LTX recording."""

import json
from typing import ClassVar
from ...models import MODELS
from ...language import translate
from ..transport import Transport
from ..events import SessionEvents
from ...state.settings import Settings
from ...state.session import RecordingWindow
from ...errors import ErrorCode, ConnectorError
from ...state.generation.ltx import LtxSpeakRequest
from ...media.units import convert_mebibytes_to_bytes
from ..inputs import VideoInputOperation, validate_capture_inputs
from ....config.generation.speech import (
    MIN_SPEECH_SECONDS,
    MAX_SCENE_CHARACTERS,
    MAX_WORDS_PER_MINUTE,
    MIN_WORDS_PER_MINUTE,
    MAX_SCRIPT_CHARACTERS,
    RECORDING_TAIL_SECONDS,
)


class LtxSpeakOperation(VideoInputOperation[LtxSpeakRequest]):
    """Prepare speech and a portrait before starting one take."""

    connection_name: ClassVar[str] = MODELS["ltx2"].connection_name
    requires_audio: ClassVar[bool] = True

    def validate(self, settings: Settings) -> None:
        """Check the portrait, script, speech pace, and LTX recording limits."""
        inputs = self.inputs
        validate_capture_inputs(inputs.duration_seconds, inputs.seed, settings)
        if inputs.duration_seconds < MIN_SPEECH_SECONDS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.ltxDuration"))
        if type(inputs.prompt) is not str or len(inputs.prompt) > MAX_SCENE_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.ltxSceneLength"))
        if type(inputs.script) is not str or not inputs.script.strip() or len(inputs.script) > MAX_SCRIPT_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.speechLength"))
        if (
            type(inputs.words_per_minute) is not int
            or not MIN_WORDS_PER_MINUTE <= inputs.words_per_minute <= MAX_WORDS_PER_MINUTE
        ):
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.speechPace"))
        if (
            type(inputs.image) is not bytes
            or not inputs.image
            or len(inputs.image) > convert_mebibytes_to_bytes(settings.max_upload_megabytes)
        ):
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.portraitUploadLimit"))

    async def begin_generation(
        self, transport: Transport, events: SessionEvents, max_capture_seconds: float
    ) -> RecordingWindow:
        """Upload the portrait and script, validate the offered speech pace, and start speech."""
        del max_capture_seconds
        inputs = self.inputs
        audio = [
            track
            for track in transport.tracks
            if track.name == "main_audio" and track.kind == "audio" and track.direction == "recvonly"
        ]
        if len(audio) != 1:
            raise ConnectorError(ErrorCode.UNAVAILABLE, translate("main", "errors.ltxAudioMissing"))
        if inputs.image is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.portraitRequired"))
        reference = await events.call(
            "upload", transport.upload_file(inputs.image, name="input.png", mime_type="image/png")
        )
        await events.command_reply("set_avatar_image", {"avatar_image": reference})
        await events.command_reply("set_script", {"script": inputs.script})
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
        if not minimum <= inputs.words_per_minute <= maximum:
            raise ConnectorError(
                ErrorCode.INVALID_INPUT, translate("main", "errors.speechPaceRange", minimum=minimum, maximum=maximum)
            )
        await events.command_reply("set_wpm", {"wpm": inputs.words_per_minute})
        # Recording fragments need later media to close after the requested capture ends.
        await events.command_reply(
            "set_duration_seconds",
            {"duration_seconds": inputs.duration_seconds + RECORDING_TAIL_SECONDS},
        )
        await events.command_reply("set_seed", {"seed": inputs.seed})
        if inputs.prompt.strip():
            await events.command_reply("set_prompt", {"prompt": inputs.prompt})
        await events.command_reply("start", {})
        return RecordingWindow(0, inputs.duration_seconds)


__all__ = ["LtxSpeakOperation"]
