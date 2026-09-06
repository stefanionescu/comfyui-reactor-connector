"""Prepare a portrait and speech script for one LTX recording."""

import json
from dataclasses import dataclass
from typing import ClassVar

from ..config import Settings
from ..errors import ConnectorError, ErrorCode
from .events import SessionEvents
from .inputs import VideoInputs, validate_capture_inputs
from .transport import Transport

RECORDING_TAIL_SECONDS = 20


@dataclass(frozen=True, slots=True)
class LtxSpeakRequest(VideoInputs):
    """Keep take conditions fixed until the session owner ends the run."""

    script: str = ""
    words_per_minute: int = 140
    model_name: ClassVar[str] = "reactor/ltx2"
    requires_audio: ClassVar[bool] = True

    def validate(self, settings: Settings) -> None:
        validate_capture_inputs(self.duration_seconds, self.seed, settings)
        if self.duration_seconds < 4:
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Use at least four seconds for LTX.")
        if type(self.prompt) is not str or len(self.prompt) > 800:
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Use at most 800 scene characters.")
        if type(self.script) is not str or not self.script.strip() or len(self.script) > 10_000:
            raise ConnectorError(
                ErrorCode.INVALID_INPUT, "Enter a script of 1 to 10,000 characters."
            )
        if type(self.words_per_minute) is not int or not 1 <= self.words_per_minute <= 1000:
            raise ConnectorError(
                ErrorCode.INVALID_INPUT, "Use a positive whole-number speech pace."
            )
        if (
            type(self.image) is not bytes
            or not self.image
            or len(self.image) > settings.max_upload_megabytes * 1_048_576
        ):
            raise ConnectorError(
                ErrorCode.INVALID_INPUT, "Provide one portrait within the upload limit."
            )

    async def configure(self, transport: Transport, events: SessionEvents) -> None:
        audio = [
            track
            for track in transport.tracks
            if track.name == "main_audio"
            and track.kind == "audio"
            and track.direction == "recvonly"
        ]
        if len(audio) != 1:
            raise ConnectorError(ErrorCode.UNAVAILABLE, "This LTX deployment has no audio track.")
        if self.image is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Provide one portrait.")
        reference = await events.call(
            "upload", transport.upload_file(self.image, name="input.png", mime_type="image/png")
        )
        await events.command("set_avatar_image", {"avatar_image": reference})
        await events.command("set_script", {"script": self.script})
        state = await events.call("speech_state", events.snapshot("state_update"))
        minimum, maximum = state.get("wpm_min"), state.get("wpm_max")
        if (
            not isinstance(minimum, (int, float))
            or isinstance(minimum, bool)
            or not isinstance(maximum, (int, float))
            or isinstance(maximum, bool)
            or not 0 < minimum <= maximum <= 1000
            or minimum != int(minimum)
            or maximum != int(maximum)
        ):
            raise ConnectorError(
                ErrorCode.UNAVAILABLE,
                "LTX did not report its accepted speech pace.",
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
                ErrorCode.INVALID_INPUT, f"Use a speech pace from {minimum} to {maximum}."
            )
        await events.command("set_wpm", {"wpm": self.words_per_minute})
        # Recording fragments need later media to close after the requested capture ends.
        await events.command(
            "set_duration_seconds",
            {"duration_seconds": self.duration_seconds + RECORDING_TAIL_SECONDS},
        )
        await events.command("set_seed", {"seed": self.seed})
        if self.prompt.strip():
            await events.command("set_prompt", {"prompt": self.prompt})
        await events.command("start", {})
