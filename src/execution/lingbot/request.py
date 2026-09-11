"""Convert camera directions into commands supported by LingBot."""

import math
from typing import ClassVar
from ..inputs import VideoInputs
from ...language import translate
from ..transport import Transport
from dataclasses import dataclass
from ..events import SessionEvents
from ...model_registry import MODELS
from ..operation import RecordingWindow
from ...settings.settings import Settings
from ...errors import ErrorCode, ConnectorError
from ....config.generation.world import (
    CAMERA_AXES,
    DEFAULT_LATERAL,
    DEFAULT_MOVEMENT,
    WORLD_FRAME_RATE,
    MAX_ROTATION_SPEED,
    MIN_ROTATION_SPEED,
    DEFAULT_LOOK_VERTICAL,
    DEFAULT_LOOK_HORIZONTAL,
    DEFAULT_ROTATION_DEGREES,
    MAX_WORLD_PROMPT_CHARACTERS,
)


@dataclass(frozen=True, slots=True)
class LingBotRequest(VideoInputs):
    """Generate from an image while holding the selected camera controls.

    Attributes:
        movement: Selected camera movement.
        look_horizontal: Horizontal camera direction.
        look_vertical: Vertical camera direction.
        rotation_speed_deg: Camera rotation speed in degrees per second.
        movement_values: Movement commands accepted by this model.

    """

    movement: str = DEFAULT_MOVEMENT
    look_horizontal: str = DEFAULT_LOOK_HORIZONTAL
    look_vertical: str = DEFAULT_LOOK_VERTICAL
    rotation_speed_deg: float = DEFAULT_ROTATION_DEGREES
    model_name: ClassVar[str] = MODELS["lingbot"].connection_name
    movement_values: ClassVar[tuple[str, ...]] = CAMERA_AXES["movement"]

    def axes(self) -> tuple[tuple[str, str], ...]:
        """Map camera directions to the command names used by LingBot."""
        return (
            ("movement", self.movement),
            ("look_horizontal", self.look_horizontal),
            ("look_vertical", self.look_vertical),
        )

    def validate(self, settings: Settings) -> None:
        """Require an image, supported directions, and a finite camera rotation speed."""
        VideoInputs.validate(self, settings)
        if self.image is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.startingImageRequired"))
        if len(self.prompt) > MAX_WORLD_PROMPT_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.worldPromptLength"))
        allowed = (
            (self.movement, self.movement_values),
            (self.look_horizontal, CAMERA_AXES["look_horizontal"]),
            (self.look_vertical, CAMERA_AXES["look_vertical"]),
        )
        if any(type(value) is not str or value not in choices for value, choices in allowed):
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.cameraDirection"))
        speed = self.rotation_speed_deg
        if (
            type(speed) not in (int, float)
            or not math.isfinite(speed)
            or not MIN_ROTATION_SPEED <= speed <= MAX_ROTATION_SPEED
        ):
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.rotationSpeed"))

    async def configure(
        self, transport: Transport, events: SessionEvents, max_capture_seconds: float
    ) -> RecordingWindow:
        """Upload the starting image, set camera controls, and start the scene."""
        del max_capture_seconds
        if self.image is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.startingImageRequired"))
        await events.command_reply("set_seed", {"seed": self.seed})
        reference = await transport.upload_file(self.image, name="input.png", mime_type="image/png")
        await events.command_reply("set_image", {"image": reference})
        await events.command_reply("set_prompt", {"prompt": self.prompt})
        await events.command_reply("set_rotation_speed_deg", {"rotation_speed_deg": self.rotation_speed_deg})
        for axis, value in self.axes():
            await events.command_reply(f"set_{axis}", {axis: value})
        await events.command_reply("start", {})
        return RecordingWindow(0, self.duration_seconds)

    async def release(self, transport: Transport) -> None:
        """Release held axes before disconnect; disconnect still runs if release fails."""
        if transport.status == "ready":
            for axis, _ in self.axes():
                await transport.send_command(f"set_{axis}", {axis: "idle"})


@dataclass(frozen=True, slots=True)
class LingBotWorldRequest(LingBotRequest):
    """Keep longitudinal and lateral movement independent for World 2.

    Attributes:
        lateral: Independent lateral camera movement.

    """

    lateral: str = DEFAULT_LATERAL
    model_name: ClassVar[str] = MODELS["lingbot-world-2"].connection_name
    fallback_fps: ClassVar[int] = WORLD_FRAME_RATE
    movement_values: ClassVar[tuple[str, ...]] = CAMERA_AXES["move_longitudinal"]

    def validate(self, settings: Settings) -> None:
        """Check the shared camera settings and World 2 lateral direction."""
        LingBotRequest.validate(self, settings)
        if type(self.lateral) is not str or self.lateral not in CAMERA_AXES["move_lateral"]:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.lateralDirection"))

    def axes(self) -> tuple[tuple[str, str], ...]:
        """Map camera directions to the command names used by LingBot World 2."""
        return (
            ("move_longitudinal", self.movement),
            ("move_lateral", self.lateral),
            ("look_horizontal", self.look_horizontal),
            ("look_vertical", self.look_vertical),
        )
