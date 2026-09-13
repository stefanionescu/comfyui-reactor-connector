"""Declare LingBot image inputs, camera controls, and video outputs."""

from comfy_api.latest import io
from ..controls import video_outputs, generation_controls
from ....config.generation.world import (
    CAMERA_AXES,
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
    movement = list(CAMERA_AXES["move_longitudinal" if world2 else "movement"])
    controls: list[io.Input] = [
        io.Combo.Input(
            "movement",
            display_name="movement",
            tooltip="Keep moving in this direction while recording. Choose idle to stay in place.",
            options=movement,
            default=DEFAULT_MOVEMENT,
        ),
    ]
    if world2:
        controls.append(
            io.Combo.Input(
                "lateral",
                display_name="sideways movement",
                tooltip="Sideways movement combines with forward or backward movement.",
                options=OPTIONS_LATERAL,
                default=DEFAULT_LATERAL,
            )
        )
    controls.extend(
        [
            io.Combo.Input(
                "look_horizontal",
                display_name="turn left or right",
                tooltip="Keep turning the camera left or right while recording.",
                options=OPTIONS_LOOK_HORIZONTAL,
                default=DEFAULT_LOOK_HORIZONTAL,
            ),
            io.Combo.Input(
                "look_vertical",
                display_name="look up or down",
                tooltip="Keep looking up or down while recording.",
                options=OPTIONS_LOOK_VERTICAL,
                default=DEFAULT_LOOK_VERTICAL,
            ),
            io.Float.Input(
                "rotation_speed_deg",
                display_name="turn per step (degrees)",
                tooltip=(
                    "Degrees per latent frame, an internal model step. Larger values turn faster; 0 stops turning."
                ),
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
    model = "LingBot World 2" if world2 else "LingBot"
    return io.Schema(
        node_id="ReactorIncLingBotWorld2Explore" if world2 else "ReactorIncLingBotExplore",
        display_name=f"{model}: Explore an Image (Reactor)",
        description="Move through a scene from your image and save a video. Choose how long to record.",
        category="Reactor/Worlds",
        search_aliases=["Reactor", model, "camera", "world", "image to video"],
        inputs=[
            io.Image.Input(
                "image",
                display_name="starting image",
                tooltip="Upload one image to use as the starting scene.",
            ),
            *generation_controls(),
            *_directions(world2=world2),
            io.Boolean.Input(
                "interactive",
                display_name="live controls",
                tooltip="Move with keys or buttons and edit the scene prompt. The camera starts still.",
                default=False,
                optional=True,
            ),
        ],
        outputs=video_outputs(),
    )
