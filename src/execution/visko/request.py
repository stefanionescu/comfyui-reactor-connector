"""Prepare image and sound settings before starting a Visko recording."""

from __future__ import annotations

import asyncio
from ...models import MODELS
from ...language import translate
from ..inputs import VideoInputOperation
from ...errors import ErrorCode, ConnectorError
from typing import cast, ClassVar, TYPE_CHECKING
from ...state.generation.visko import ViskoStableRequest
from ...state.session import ControlValues, RecordingWindow
from ....config.generation.video import MAX_FORMAT_NAME_CHARACTERS, MAX_AUDIO_PROMPT_CHARACTERS

if TYPE_CHECKING:
    from ..transport import Transport
    from ..events import SessionEvents
    from ...state.settings import Settings


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


class ViskoStableOperation(VideoInputOperation[ViskoStableRequest]):
    """Generate synchronized video and audio using the provider's recording clock."""

    connection_name: ClassVar[str] = MODELS["visko-orbis-stable"].connection_name
    requires_audio: ClassVar[bool] = True

    def validate(self, settings: Settings) -> None:
        """Check image, sound prompt, resolution, and boolean options."""
        super().validate(settings)
        inputs = self.inputs
        if type(inputs.audio_prompt) is not str or len(inputs.audio_prompt) > MAX_AUDIO_PROMPT_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.soundPromptLength"))
        if type(inputs.resolution) is not str or len(inputs.resolution) > MAX_FORMAT_NAME_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.resolutionName"))
        if type(inputs.audio_enabled) is not bool or type(inputs.prompt_passthrough) is not bool:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.soundOptionType"))

    def build_control_values(self) -> ControlValues:
        """Return sound and passthrough values selected for live controls."""
        return ControlValues(
            self.inputs.prompt,
            is_passthrough_enabled=self.inputs.prompt_passthrough,
            audio_prompt=self.inputs.audio_prompt,
            is_audio_enabled=self.inputs.audio_enabled,
        )

    async def begin_generation(
        self, transport: Transport, events: SessionEvents, max_capture_seconds: float
    ) -> RecordingWindow:
        """Set image and sound options, start generation, and confirm the accepted settings."""
        del max_capture_seconds
        inputs = self.inputs
        tracks = [
            track
            for track in transport.tracks
            if track.name == "main_audio" and track.kind == "audio" and track.direction == "recvonly"
        ]
        if len(tracks) != 1:
            raise ConnectorError(ErrorCode.UNAVAILABLE, translate("main", "errors.viskoAudioMissing"))
        started = ViskoStart(events)
        await events.command_reply("set_seed", {"seed": inputs.seed})
        if inputs.image is not None:
            reference = await events.call(
                "upload", transport.upload_file(inputs.image, name="input.png", mime_type="image/png")
            )
            await events.command_reply("set_image", {"image": reference})
        await events.command_reply("set_audio_enabled", {"audio_enabled": inputs.audio_enabled})
        await events.command_reply("set_audio_prompt", {"prompt": inputs.audio_prompt})
        await events.command_reply("set_prompt", {"prompt": inputs.prompt, "passthrough": inputs.prompt_passthrough})
        if inputs.resolution:
            # The generated seed setter may emit nothing. Condition commands emit state.
            await events.call("resolution_state", events.state_ready.wait())
            offered = events.state.get("available_resolutions")
            if not isinstance(offered, list) or inputs.resolution not in offered:
                raise ConnectorError(
                    ErrorCode.INVALID_INPUT,
                    translate("main", "errors.resolutionUnavailable"),
                )
            await events.command_reply("set_resolution", {"resolution": inputs.resolution})
        await events.command_reply("start", {})
        await events.call(
            "generation_started",
            started.confirm(
                has_image=inputs.image is not None,
                is_sound_enabled=inputs.audio_enabled,
                resolution=inputs.resolution,
            ),
        )
        return RecordingWindow(0, inputs.duration_seconds)


class ViskoDynamicOperation(ViskoStableOperation):
    """Keep Dynamic's canonical identity separate from Stable's saved workflows."""

    connection_name: ClassVar[str] = MODELS["visko-orbis-dynamic"].connection_name


__all__ = ["ViskoDynamicOperation", "ViskoStableOperation"]
