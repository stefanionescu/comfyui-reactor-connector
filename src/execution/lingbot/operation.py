"""Convert camera directions into commands supported by LingBot."""

import math
from typing import ClassVar
from ...models import MODELS
from ...language import translate
from ..transport import Transport
from ..events import SessionEvents
from ...state.settings import Settings
from ..inputs import VideoInputOperation
from ...state.session import RecordingWindow
from ...errors import ErrorCode, ConnectorError
from ...state.generation.lingbot import LingBotRequest, LingBotWorldRequest
from ....config.generation.world import (
    CAMERA_AXES,
    WORLD_FRAME_RATE,
    MAX_ROTATION_SPEED,
    MIN_ROTATION_SPEED,
    MAX_WORLD_PROMPT_CHARACTERS,
)


class LingBotOperation(VideoInputOperation[LingBotRequest]):
    """Hold the requested camera controls while generating from an image."""

    connection_name: ClassVar[str] = MODELS["lingbot"].connection_name
    movement_values: ClassVar[tuple[str, ...]] = CAMERA_AXES["movement"]

    def axes(self) -> tuple[tuple[str, str], ...]:
        """Map camera directions to the command names used by LingBot."""
        return (
            ("movement", self.inputs.movement),
            ("look_horizontal", self.inputs.look_horizontal),
            ("look_vertical", self.inputs.look_vertical),
        )

    def validate(self, settings: Settings) -> None:
        """Require an image, supported directions, and a finite camera rotation speed."""
        super().validate(settings)
        inputs = self.inputs
        if inputs.image is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.startingImageRequired"))
        if len(inputs.prompt) > MAX_WORLD_PROMPT_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.worldPromptLength"))
        allowed = (
            (inputs.movement, self.movement_values),
            (inputs.look_horizontal, CAMERA_AXES["look_horizontal"]),
            (inputs.look_vertical, CAMERA_AXES["look_vertical"]),
        )
        if any(type(value) is not str or value not in choices for value, choices in allowed):
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.cameraDirection"))
        speed = inputs.rotation_speed_deg
        if (
            type(speed) not in (int, float)
            or not math.isfinite(speed)
            or not MIN_ROTATION_SPEED <= speed <= MAX_ROTATION_SPEED
        ):
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.rotationSpeed"))

    async def begin_generation(
        self, transport: Transport, events: SessionEvents, max_capture_seconds: float
    ) -> RecordingWindow:
        """Upload the starting image, set camera controls, and start the scene."""
        del max_capture_seconds
        inputs = self.inputs
        if inputs.image is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.startingImageRequired"))
        await events.command_reply("set_seed", {"seed": inputs.seed})
        reference = await transport.upload_file(inputs.image, name="input.png", mime_type="image/png")
        await events.command_reply("set_image", {"image": reference})
        await events.command_reply("set_prompt", {"prompt": inputs.prompt})
        await events.command_reply("set_rotation_speed_deg", {"rotation_speed_deg": inputs.rotation_speed_deg})
        for axis, value in self.axes():
            await events.command_reply(f"set_{axis}", {axis: value})
        await events.command_reply("start", {})
        return RecordingWindow(0, inputs.duration_seconds)

    async def release(self, transport: Transport) -> None:
        """Release held axes before disconnect; disconnect still runs if release fails."""
        if transport.status == "ready":
            for axis, _ in self.axes():
                await transport.send_command(f"set_{axis}", {axis: "idle"})


class LingBotWorldOperation(LingBotOperation):
    """Hold longitudinal and lateral camera controls independently for World 2.

    Attributes:
        lateral: Requested sideways camera direction.

    """

    connection_name: ClassVar[str] = MODELS["lingbot-world-2"].connection_name
    fallback_fps: ClassVar[int] = WORLD_FRAME_RATE
    movement_values: ClassVar[tuple[str, ...]] = CAMERA_AXES["move_longitudinal"]

    def __init__(self, inputs: LingBotWorldRequest) -> None:
        """Keep the World 2 sideways direction beside the shared camera inputs."""
        super().__init__(inputs)
        self.lateral = inputs.lateral

    def validate(self, settings: Settings) -> None:
        """Check the shared camera settings and World 2 lateral direction."""
        super().validate(settings)
        if type(self.lateral) is not str or self.lateral not in CAMERA_AXES["move_lateral"]:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.lateralDirection"))

    def axes(self) -> tuple[tuple[str, str], ...]:
        """Map camera directions to the command names used by LingBot World 2."""
        return (
            ("move_longitudinal", self.inputs.movement),
            ("move_lateral", self.lateral),
            ("look_horizontal", self.inputs.look_horizontal),
            ("look_vertical", self.inputs.look_vertical),
        )


__all__ = ["LingBotOperation", "LingBotWorldOperation"]
