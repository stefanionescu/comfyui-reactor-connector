"""Declare LingBot image inputs, camera controls, and video outputs."""

from comfy_api.latest import io
from ..schema import translate_schema
from ..controls import video_outputs, generation_controls
from ....config.generation.world import (
    DEFAULT_LATERAL,
    OPTIONS_LATERAL,
    DEFAULT_MOVEMENT,
    MAX_ROTATION_SPEED,
    MIN_ROTATION_SPEED,
    DEFAULT_LOOK_VERTICAL,
    OPTIONS_LOOK_VERTICAL,
    STEP_ROTATION_DEGREES,
    DEFAULT_LOOK_HORIZONTAL,
    OPTIONS_LOOK_HORIZONTAL,
    DEFAULT_ROTATION_DEGREES,
)


def _directions(*, world2: bool) -> list[io.Input]:
    """Build movement and rotation controls for the selected LingBot version."""
    movement = ["idle", "forward", "back"]
    if not world2:
        movement.extend(["strafe_left", "strafe_right"])
    controls: list[io.Input] = [
        io.Combo.Input(
            "movement",
            options=movement,
            default=DEFAULT_MOVEMENT,
        ),
    ]
    if world2:
        controls.append(
            io.Combo.Input(
                "lateral",
                options=OPTIONS_LATERAL,
                default=DEFAULT_LATERAL,
            )
        )
    controls.extend(
        [
            io.Combo.Input(
                "look_horizontal",
                options=OPTIONS_LOOK_HORIZONTAL,
                default=DEFAULT_LOOK_HORIZONTAL,
            ),
            io.Combo.Input(
                "look_vertical",
                options=OPTIONS_LOOK_VERTICAL,
                default=DEFAULT_LOOK_VERTICAL,
            ),
            io.Float.Input(
                "rotation_speed_deg",
                default=DEFAULT_ROTATION_DEGREES,
                min=MIN_ROTATION_SPEED,
                max=MAX_ROTATION_SPEED,
                step=STEP_ROTATION_DEGREES,
            ),
        ]
    )
    return controls


def lingbot_schema(*, world2: bool) -> io.Schema:
    """Declare the selected LingBot node with its image, camera controls, and outputs."""
    return translate_schema(
        io.Schema(
            node_id="ReactorIncLingBotWorld2Explore" if world2 else "ReactorIncLingBotExplore",
            inputs=[
                io.Image.Input(
                    "image",
                ),
                *generation_controls(),
                *_directions(world2=world2),
                io.Boolean.Input(
                    "interactive",
                    default=False,
                    optional=True,
                ),
            ],
            outputs=video_outputs(),
        )
    )
