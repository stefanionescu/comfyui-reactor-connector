"""Convert camera directions into commands supported by LingBot."""

import math
from dataclasses import dataclass
from typing import ClassVar

from ..config import Settings
from ..errors import ConnectorError, ErrorCode
from .events import SessionEvents
from .inputs import VideoInputs
from .transport import Transport


@dataclass(frozen=True, slots=True)
class LingBotRequest(VideoInputs):
    """Generate from an image while holding the selected camera controls."""

    movement: str = "idle"
    look_horizontal: str = "idle"
    look_vertical: str = "idle"
    rotation_speed_deg: float = 5.0
    model_name: ClassVar[str] = "reactor/lingbot"
    movement_values: ClassVar[tuple[str, ...]] = (
        "idle",
        "forward",
        "back",
        "strafe_left",
        "strafe_right",
    )

    def axes(self) -> tuple[tuple[str, str], ...]:
        return (
            ("movement", self.movement),
            ("look_horizontal", self.look_horizontal),
            ("look_vertical", self.look_vertical),
        )

    def validate(self, settings: Settings) -> None:
        VideoInputs.validate(self, settings)
        if self.image is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Connect one starting image.")
        if len(self.prompt) > 1000:
            raise ConnectorError(
                ErrorCode.INVALID_INPUT, "Use a prompt of at most 1,000 characters."
            )
        allowed = (
            (self.movement, self.movement_values),
            (self.look_horizontal, ("idle", "left", "right")),
            (self.look_vertical, ("idle", "up", "down")),
        )
        if any(type(value) is not str or value not in choices for value, choices in allowed):
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Choose a listed camera direction.")
        speed = self.rotation_speed_deg
        if type(speed) not in (int, float) or not math.isfinite(speed) or not 0 <= speed <= 30:
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Choose a rotation speed from 0 to 30.")

    async def configure(self, transport: Transport, events: SessionEvents) -> None:
        if self.image is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Connect one starting image.")
        await events.command("set_seed", {"seed": self.seed})
        reference = await transport.upload_file(self.image, name="input.png", mime_type="image/png")
        await events.command("set_image", {"image": reference})
        await events.command("set_prompt", {"prompt": self.prompt})
        await events.command(
            "set_rotation_speed_deg", {"rotation_speed_deg": self.rotation_speed_deg}
        )
        for axis, value in self.axes():
            await events.command(f"set_{axis}", {axis: value})
        await events.command("start", {})

    async def release(self, transport: Transport) -> None:
        """Release held axes before disconnect; disconnect still runs if release fails."""
        if transport.status == "ready":
            for axis, _ in self.axes():
                await transport.send_command(f"set_{axis}", {axis: "idle"})


@dataclass(frozen=True, slots=True)
class LingBotWorld2Request(LingBotRequest):
    """Keep longitudinal and lateral movement independent for World 2."""

    lateral: str = "idle"
    model_name: ClassVar[str] = "reactor/lingbot-world-2"
    fallback_fps: ClassVar[int] = 48
    movement_values: ClassVar[tuple[str, ...]] = ("idle", "forward", "back")

    def validate(self, settings: Settings) -> None:
        LingBotRequest.validate(self, settings)
        if type(self.lateral) is not str or self.lateral not in (
            "idle",
            "strafe_left",
            "strafe_right",
        ):
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Choose a listed lateral direction.")

    def axes(self) -> tuple[tuple[str, str], ...]:
        return (
            ("move_longitudinal", self.movement),
            ("move_lateral", self.lateral),
            ("look_horizontal", self.look_horizontal),
            ("look_vertical", self.look_vertical),
        )
