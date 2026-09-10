"""Prepare image and sound settings before starting a Visko recording."""

import asyncio
from ..inputs import VideoInputs
from ...language import translate
from ..transport import Transport
from dataclasses import dataclass
from typing import cast, ClassVar
from ..events import SessionEvents
from ...settings.settings import Settings
from ...errors import ErrorCode, ConnectorError
from ....config.models.identities import IDENTITIES
from ....config.generation.video import MAX_FORMAT_NAME_CHARACTERS, MAX_AUDIO_PROMPT_CHARACTERS


class ViskoStart:
    """Check that generation starts with the requested image and sound settings."""

    def __init__(self, events: SessionEvents) -> None:
        """Subscribe to generation-start messages until the session closes."""
        self.started = asyncio.Event()
        self.settings: dict[str, object] = {}
        events.transport.on("message", self.observe)
        events.handlers.append(("message", self.observe))

    def observe(self, message: object) -> None:
        """Capture the model settings reported when generation starts."""
        if not isinstance(message, dict):
            return
        envelope = cast("dict[str, object]", message)
        if envelope.get("type") != "generation_started":
            return
        payload = envelope.get("data")
        if isinstance(payload, dict):
            self.settings = cast("dict[str, object]", payload)
        self.started.set()

    async def confirm(self, *, has_image: bool, is_sound_enabled: bool, resolution: str) -> None:
        """Wait for generation and require the requested image, sound, and resolution settings."""
        await self.started.wait()
        if self.settings.get("image_conditioned") is not has_image:
            raise ConnectorError(
                ErrorCode.UNAVAILABLE,
                translate("main", "errors.viskoImageChanged"),
            )
        if self.settings.get("audio_enabled") is not is_sound_enabled:
            raise ConnectorError(
                ErrorCode.UNAVAILABLE,
                translate("main", "errors.viskoSoundChanged"),
            )
        if resolution and self.settings.get("resolution") != resolution:
            raise ConnectorError(
                ErrorCode.UNAVAILABLE,
                translate("main", "errors.viskoResolutionChanged"),
            )


@dataclass(frozen=True, slots=True)
class ViskoStableRequest(VideoInputs):
    """Generate synchronized video and audio using the provider's recording clock."""

    audio_prompt: str = ""
    resolution: str = ""
    audio_enabled: bool = True
    prompt_passthrough: bool = False
    model_name: ClassVar[str] = IDENTITIES["visko-orbis-stable"][1]
    requires_audio: ClassVar[bool] = True

    def validate(self, settings: Settings) -> None:
        """Check image, sound prompt, resolution, and boolean options."""
        super(ViskoStableRequest, self).validate(settings)
        if type(self.audio_prompt) is not str or len(self.audio_prompt) > MAX_AUDIO_PROMPT_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.soundPromptLength"))
        if type(self.resolution) is not str or len(self.resolution) > MAX_FORMAT_NAME_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.resolutionName"))
        if type(self.audio_enabled) is not bool or type(self.prompt_passthrough) is not bool:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.soundOptionType"))

    async def configure(self, transport: Transport, events: SessionEvents) -> None:
        """Set image and sound options, start generation, and confirm the accepted settings."""
        tracks = [
            track
            for track in transport.tracks
            if track.name == "main_audio" and track.kind == "audio" and track.direction == "recvonly"
        ]
        if len(tracks) != 1:
            raise ConnectorError(ErrorCode.UNAVAILABLE, translate("main", "errors.viskoAudioMissing"))
        started = ViskoStart(events)
        await events.command_reply("set_seed", {"seed": self.seed})
        if self.image is not None:
            reference = await events.call(
                "upload", transport.upload_file(self.image, name="input.png", mime_type="image/png")
            )
            await events.command_reply("set_image", {"image": reference})
        await events.command_reply("set_audio_enabled", {"audio_enabled": self.audio_enabled})
        await events.command_reply("set_audio_prompt", {"prompt": self.audio_prompt})
        await events.command_reply("set_prompt", {"prompt": self.prompt, "passthrough": self.prompt_passthrough})
        if self.resolution:
            # The generated seed setter may emit nothing. Condition commands emit state.
            await events.call("resolution_state", events.state_ready.wait())
            offered = events.state.get("available_resolutions")
            if not isinstance(offered, list) or self.resolution not in offered:
                raise ConnectorError(
                    ErrorCode.INVALID_INPUT,
                    translate("main", "errors.resolutionUnavailable"),
                )
            await events.command_reply("set_resolution", {"resolution": self.resolution})
        await events.command_reply("start", {})
        await events.call(
            "generation_started",
            started.confirm(
                has_image=self.image is not None,
                is_sound_enabled=self.audio_enabled,
                resolution=self.resolution,
            ),
        )


@dataclass(frozen=True, slots=True)
class ViskoDynamicRequest(ViskoStableRequest):
    """Keep Dynamic's canonical identity separate from Stable's saved workflows."""

    model_name: ClassVar[str] = IDENTITIES["visko-orbis-dynamic"][1]
