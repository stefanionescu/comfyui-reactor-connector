"""Declare the LingBot inputs and camera controls, and build the operation that each version records."""

from typing import TypedDict, NotRequired
import asyncio

from comfy_api.latest import Input, io

from ..controls import build_inputs
from ...media.images import encode_png
from ...config.generation.world import (
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
from ...state.generation.lingbot import LingBotRequest, LingBotWorldRequest
from ...execution.lingbot.operation import LingBotOperation, LingBotWorldOperation

IMAGE_TOOLTIP = 'Upload one image to use as the starting scene.'


class LingBotInputs(TypedDict):
    """The saved inputs that ComfyUI passes to the LingBot node, apart from the run number.

    Attributes:
        image: Starting image of the scene.
        prompt: Scene prompt.
        duration_seconds: Requested recording length in seconds.
        seed: Random seed sent to the model.

        movement: Direction the camera keeps moving in.
        look_horizontal: Direction the camera keeps turning: left, right, or idle.
        look_vertical: Direction the camera keeps looking: up, down, or idle.
        rotation_speed_deg: Camera turn in degrees per latent frame, an internal model step.
        interactive: Whether live controls replace the held directions.

    """

    image: Input.Image
    prompt: str
    duration_seconds: float
    seed: int
    movement: str
    look_horizontal: str
    look_vertical: str
    rotation_speed_deg: float
    interactive: NotRequired[bool]


class LingBotWorldInputs(LingBotInputs):
    """The saved inputs of the LingBot World 2 node, which adds sideways movement.

    Attributes:
        lateral: Sideways direction the camera keeps moving in.

    """

    lateral: str


class _RequestFields(TypedDict):
    """The request values that both LingBot versions take."""

    prompt: str
    duration_seconds: float
    seed: int
    image: bytes | None
    movement: str
    look_horizontal: str
    look_vertical: str
    rotation_speed_deg: float


def lingbot_inputs(*, is_world_two: bool) -> list[io.Input]:
    """List the starting image, the shared controls, and the camera controls of the selected LingBot version."""
    directions: list[io.Input] = [
        io.Combo.Input(
            'movement',
            display_name='movement',
            tooltip='Keep moving in this direction while recording. Choose idle to stay in place.',
            options=list(CAMERA_AXES['move_longitudinal' if is_world_two else 'movement']),
            default=DEFAULT_MOVEMENT,
        ),
    ]
    if is_world_two:
        directions.append(
            io.Combo.Input(
                'lateral',
                display_name='sideways movement',
                tooltip='Sideways movement combines with forward or backward movement.',
                options=OPTIONS_LATERAL,
                default=DEFAULT_LATERAL,
            )
        )
    return build_inputs(
        leading=[io.Image.Input('image', display_name='starting image', tooltip=IMAGE_TOOLTIP)],
        trailing=[
            *directions,
            io.Combo.Input(
                'look_horizontal',
                display_name='turn left or right',
                tooltip='Keep turning the camera left or right while recording.',
                options=OPTIONS_LOOK_HORIZONTAL,
                default=DEFAULT_LOOK_HORIZONTAL,
            ),
            io.Combo.Input(
                'look_vertical',
                display_name='look up or down',
                tooltip='Keep looking up or down while recording.',
                options=OPTIONS_LOOK_VERTICAL,
                default=DEFAULT_LOOK_VERTICAL,
            ),
            io.Float.Input(
                'rotation_speed_deg',
                display_name='turn per step (degrees)',
                tooltip='Degrees per latent frame, an internal model step. Larger values turn faster; 0 stops turning.',
                default=DEFAULT_ROTATION_DEGREES,
                min=MIN_ROTATION_SPEED,
                max=MAX_ROTATION_SPEED,
                step=STEP_ROTATION_DEGREES,
            ),
            io.Boolean.Input(
                'interactive',
                display_name='live controls',
                tooltip='Move with keys or buttons and edit the scene prompt. The camera starts still.',
                default=False,
                optional=True,
            ),
        ],
    )


async def build_operation(
    inputs: LingBotInputs, *, interactive: bool, lateral: str | None
) -> LingBotOperation[LingBotRequest] | LingBotWorldOperation:
    """Encode the starting image and build the operation of the selected LingBot version.

    Live controls start with the camera still, so they replace each held direction with idle. A sideways direction
    selects World 2.
    """
    fields = _RequestFields(
        prompt=inputs['prompt'],
        duration_seconds=inputs['duration_seconds'],
        seed=inputs['seed'],
        image=await asyncio.to_thread(encode_png, inputs['image']),
        movement='idle' if interactive else inputs['movement'],
        look_horizontal='idle' if interactive else inputs['look_horizontal'],
        look_vertical='idle' if interactive else inputs['look_vertical'],
        rotation_speed_deg=inputs['rotation_speed_deg'],
    )
    if lateral is None:
        return LingBotOperation(LingBotRequest(**fields))
    return LingBotWorldOperation(LingBotWorldRequest(**fields, lateral='idle' if interactive else lateral))
