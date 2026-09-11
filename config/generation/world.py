"""World navigation controls, prompt limits, and camera defaults."""

MAX_WORLD_PROMPT_CHARACTERS = 1000

MAX_ROTATION_SPEED = 30

MIN_ROTATION_SPEED = 0.0

WORLD_FRAME_RATE = 48

DEFAULT_MOVEMENT = "idle"

LATERAL_VALUES = ("idle", "strafe_left", "strafe_right")

OPTIONS_LATERAL = [*LATERAL_VALUES]

DEFAULT_LATERAL = "idle"

LOOK_HORIZONTAL_VALUES = ("idle", "left", "right")

OPTIONS_LOOK_HORIZONTAL = [*LOOK_HORIZONTAL_VALUES]

DEFAULT_LOOK_HORIZONTAL = "idle"

LOOK_VERTICAL_VALUES = ("idle", "up", "down")

OPTIONS_LOOK_VERTICAL = [*LOOK_VERTICAL_VALUES]

DEFAULT_LOOK_VERTICAL = "idle"

DEFAULT_ROTATION_DEGREES = 5.0

STEP_ROTATION_DEGREES = 0.1

LINGBOT_CAMERA_AXES = ("movement", "look_horizontal", "look_vertical")

LINGBOT_WORLD_CAMERA_AXES = ("move_longitudinal", "move_lateral", "look_horizontal", "look_vertical")

CAMERA_AXES = {
    "movement": ("idle", "forward", "back", "strafe_left", "strafe_right"),
    "move_longitudinal": ("idle", "forward", "back"),
    "move_lateral": LATERAL_VALUES,
    "look_horizontal": LOOK_HORIZONTAL_VALUES,
    "look_vertical": LOOK_VERTICAL_VALUES,
}

__all__ = [
    "CAMERA_AXES",
    "DEFAULT_LATERAL",
    "DEFAULT_LOOK_HORIZONTAL",
    "DEFAULT_LOOK_VERTICAL",
    "DEFAULT_MOVEMENT",
    "DEFAULT_ROTATION_DEGREES",
    "LATERAL_VALUES",
    "LINGBOT_CAMERA_AXES",
    "LINGBOT_WORLD_CAMERA_AXES",
    "LOOK_HORIZONTAL_VALUES",
    "LOOK_VERTICAL_VALUES",
    "MAX_ROTATION_SPEED",
    "MAX_WORLD_PROMPT_CHARACTERS",
    "MIN_ROTATION_SPEED",
    "OPTIONS_LATERAL",
    "OPTIONS_LOOK_HORIZONTAL",
    "OPTIONS_LOOK_VERTICAL",
    "STEP_ROTATION_DEGREES",
    "WORLD_FRAME_RATE",
]
