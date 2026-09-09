"""World navigation controls, prompt limits, and camera defaults."""

MAX_WORLD_PROMPT_CHARACTERS = 1000

MAX_ROTATION_SPEED = 30

DEFAULT_MOVEMENT = "idle"

OPTIONS_LATERAL = ["idle", "strafe_left", "strafe_right"]

DEFAULT_LATERAL = "idle"

OPTIONS_LOOK_HORIZONTAL = ["idle", "left", "right"]

DEFAULT_LOOK_HORIZONTAL = "idle"

OPTIONS_LOOK_VERTICAL = ["idle", "up", "down"]

DEFAULT_LOOK_VERTICAL = "idle"

DEFAULT_ROTATION_DEGREES = 5.0

STEP_ROTATION_DEGREES = 0.1

CAMERA_AXES = {
    "movement": ("idle", "forward", "back", "strafe_left", "strafe_right"),
    "move_longitudinal": ("idle", "forward", "back"),
    "move_lateral": OPTIONS_LATERAL,
    "look_horizontal": OPTIONS_LOOK_HORIZONTAL,
    "look_vertical": OPTIONS_LOOK_VERTICAL,
}

WORLD_AXES = {
    "lingbot": ("movement", "look_horizontal", "look_vertical"),
    "lingbot-world-2": ("move_longitudinal", "move_lateral", "look_horizontal", "look_vertical"),
}

__all__ = [
    "CAMERA_AXES",
    "DEFAULT_LATERAL",
    "DEFAULT_LOOK_HORIZONTAL",
    "DEFAULT_LOOK_VERTICAL",
    "DEFAULT_MOVEMENT",
    "DEFAULT_ROTATION_DEGREES",
    "MAX_ROTATION_SPEED",
    "MAX_WORLD_PROMPT_CHARACTERS",
    "OPTIONS_LATERAL",
    "OPTIONS_LOOK_HORIZONTAL",
    "OPTIONS_LOOK_VERTICAL",
    "STEP_ROTATION_DEGREES",
    "WORLD_AXES",
]
