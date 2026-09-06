"""Prepare image and sound settings before starting a Visko recording."""

import asyncio
from dataclasses import dataclass
from typing import ClassVar, cast

from ..config import Settings
from ..errors import ConnectorError, ErrorCode
from .events import SessionEvents
from .inputs import VideoInputs
from .transport import Transport


class ViskoStart:
    """Check that generation starts with the requested image and sound settings."""

    def __init__(self, events: SessionEvents) -> None:
        self.started = asyncio.Event()
        self.settings: dict[str, object] = {}
        events.transport.on("message", self.observe)
        events.handlers.append(("message", self.observe))

    def observe(self, message: object) -> None:
        if not isinstance(message, dict):
            return
        envelope = cast(dict[str, object], message)
        if envelope.get("type") != "generation_started":
            return
        data = envelope.get("data")
        if isinstance(data, dict):
            self.settings = cast(dict[str, object], data)
        self.started.set()

    async def confirm(self, *, image: bool, sound: bool, resolution: str) -> None:
        await self.started.wait()
        if self.settings.get("image_conditioned") is not image:
            raise ConnectorError(
                ErrorCode.UNAVAILABLE,
                "Visko started with different image settings. The run was stopped.",
            )
        if self.settings.get("audio_enabled") is not sound:
            raise ConnectorError(
                ErrorCode.UNAVAILABLE,
                "Visko started with different sound settings. The run was stopped.",
            )
        if resolution and self.settings.get("resolution") != resolution:
            raise ConnectorError(
                ErrorCode.UNAVAILABLE,
                "Visko started at a different resolution. The run was stopped.",
            )


@dataclass(frozen=True, slots=True)
class ViskoStableRequest(VideoInputs):
    """Generate synchronized video and audio using the provider's recording clock."""

    audio_prompt: str = ""
    resolution: str = ""
    audio_enabled: bool = True
    prompt_passthrough: bool = False
    model_name: ClassVar[str] = "reactor/visko-orbis-stable"
    requires_audio: ClassVar[bool] = True

    def validate(self, settings: Settings) -> None:
        super(ViskoStableRequest, self).validate(settings)
        if type(self.audio_prompt) is not str or len(self.audio_prompt) > 1000:
            raise ConnectorError(
                ErrorCode.INVALID_INPUT, "Use at most 1,000 audio prompt characters."
            )
        if type(self.resolution) is not str or len(self.resolution) > 64:
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Use a short model resolution name.")
        if type(self.audio_enabled) is not bool or type(self.prompt_passthrough) is not bool:
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Use boolean sound and prompt options.")

    async def configure(self, transport: Transport, events: SessionEvents) -> None:
        tracks = [
            track
            for track in transport.tracks
            if track.name == "main_audio"
            and track.kind == "audio"
            and track.direction == "recvonly"
        ]
        if len(tracks) != 1:
            raise ConnectorError(ErrorCode.UNAVAILABLE, "This Visko deployment has no audio track.")
        started = ViskoStart(events)
        await events.command("set_seed", {"seed": self.seed})
        if self.image is not None:
            reference = await events.call(
                "upload", transport.upload_file(self.image, name="input.png", mime_type="image/png")
            )
            await events.command("set_image", {"image": reference})
        await events.command("set_audio_enabled", {"audio_enabled": self.audio_enabled})
        await events.command("set_audio_prompt", {"prompt": self.audio_prompt})
        await events.command(
            "set_prompt", {"prompt": self.prompt, "passthrough": self.prompt_passthrough}
        )
        if self.resolution:
            # The generated seed setter may emit nothing. Condition commands emit state.
            await events.call("resolution_state", events.state_ready.wait())
            offered = events.state.get("available_resolutions")
            if not isinstance(offered, list) or self.resolution not in offered:
                raise ConnectorError(
                    ErrorCode.INVALID_INPUT,
                    "This model does not offer that resolution. Leave it blank for the default.",
                )
            await events.command("set_resolution", {"resolution": self.resolution})
        await events.command("start", {})
        await events.call(
            "generation_started",
            started.confirm(
                image=self.image is not None,
                sound=self.audio_enabled,
                resolution=self.resolution,
            ),
        )


@dataclass(frozen=True, slots=True)
class ViskoDynamicRequest(ViskoStableRequest):
    """Keep Dynamic's canonical identity separate from Stable's saved workflows."""

    model_name: ClassVar[str] = "reactor/visko-orbis-dynamic"
