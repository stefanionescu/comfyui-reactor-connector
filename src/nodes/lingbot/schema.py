"""Declare LingBot image inputs, camera controls, and video outputs."""

from comfy_api.latest import io
from ..controls import video_outputs, generation_controls
from ....config.generation.world import MAX_ROTATION_SPEED, STEP_ROTATION_DEGREES, DEFAULT_ROTATION_DEGREES
from ....config.generation.world import (
    DEFAULT_LATERAL,
    OPTIONS_LATERAL,
    DEFAULT_MOVEMENT,
    DEFAULT_LOOK_VERTICAL,
    OPTIONS_LOOK_VERTICAL,
    DEFAULT_LOOK_HORIZONTAL,
    OPTIONS_LOOK_HORIZONTAL,
)


def _directions(*, world2: bool) -> list[io.Input]:
    """Build movement and rotation controls for the selected LingBot version."""
    movement = ["idle", "forward", "back"]
    if not world2:
        movement.extend(["strafe_left", "strafe_right"])
    controls: list[io.Input] = [
        io.Combo.Input(
            "movement",
            display_name="Movement",
            options=movement,
            default=DEFAULT_MOVEMENT,
            tooltip="Keep moving in this direction while recording. Choose idle to stay in place.",
        ),
    ]
    if world2:
        controls.append(
            io.Combo.Input(
                "lateral",
                display_name="Sideways movement",
                options=OPTIONS_LATERAL,
                default=DEFAULT_LATERAL,
                tooltip="Sideways movement combines with forward or backward movement.",
            )
        )
    controls.extend(
        [
            io.Combo.Input(
                "look_horizontal",
                display_name="Turn left or right",
                options=OPTIONS_LOOK_HORIZONTAL,
                default=DEFAULT_LOOK_HORIZONTAL,
                tooltip="Keep turning the camera left or right while recording.",
            ),
            io.Combo.Input(
                "look_vertical",
                display_name="Look up or down",
                options=OPTIONS_LOOK_VERTICAL,
                default=DEFAULT_LOOK_VERTICAL,
                tooltip="Keep looking up or down while recording.",
            ),
            io.Float.Input(
                "rotation_speed_deg",
                display_name="Turn per step (degrees)",
                default=DEFAULT_ROTATION_DEGREES,
                min=0.0,
                max=MAX_ROTATION_SPEED,
                step=STEP_ROTATION_DEGREES,
                tooltip=("Turn amount per model step, in degrees. Larger values turn faster; 0 stops turning."),
            ),
        ]
    )
    return controls


def lingbot_schema(*, world2: bool) -> io.Schema:
    """Declare the selected LingBot node with its image, camera controls, and outputs."""
    title = "LingBot World 2" if world2 else "LingBot"
    return io.Schema(
        node_id="ReactorIncLingBotWorld2Explore" if world2 else "ReactorIncLingBotExplore",
        display_name=f"Reactor {title}: Explore an image",
        category="Reactor/Worlds",
        inputs=[
            io.Image.Input(
                "image",
                display_name="Starting image",
                tooltip="Upload one image to use as the starting scene.",
            ),
            *generation_controls(),
            *_directions(world2=world2),
            io.Boolean.Input(
                "interactive",
                display_name="Live controls",
                default=False,
                optional=True,
                tooltip=("Move with keys or buttons and edit the scene prompt. The camera starts still."),
            ),
        ],
        outputs=video_outputs(),
        description=("Move through a scene from your image and save a video. Choose how long to record."),
        search_aliases=["Reactor", title, "camera", "world", "image to video"],
    )
