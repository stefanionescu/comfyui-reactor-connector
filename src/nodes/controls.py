"""Shared controls for video generation."""

from comfy_api.latest import io
from ...config.generation.prompts import DEFAULT_PROMPTS
from ...config.nodes import (
    MAX_SEED,
    DEFAULT_SEED,
    MAX_VARIATION,
    MIN_VARIATION,
    DEFAULT_VARIATION,
    MAX_DURATION_SECONDS,
    MIN_DURATION_SECONDS,
    STEP_DURATION_SECONDS,
    DEFAULT_DURATION_SECONDS,
)


def generation_controls(
    prompt_key: str = "video",
) -> list[io.Input]:
    """Build the shared prompt, duration, seed, and repeat-run controls."""
    return [
        io.String.Input(
            "prompt",
            multiline=True,
            default=DEFAULT_PROMPTS[prompt_key],
        ),
        io.Float.Input(
            "duration_seconds",
            default=DEFAULT_DURATION_SECONDS,
            min=MIN_DURATION_SECONDS,
            max=MAX_DURATION_SECONDS,
            step=STEP_DURATION_SECONDS,
        ),
        io.Int.Input(
            "seed",
            default=DEFAULT_SEED,
            min=0,
            max=MAX_SEED,
            control_after_generate=True,
        ),
        io.Int.Input(
            "variation",
            default=DEFAULT_VARIATION,
            min=MIN_VARIATION,
            max=MAX_VARIATION,
        ),
    ]


def video_outputs() -> list[io.Output]:
    """Declare the native video and recording-details output sockets."""
    return [io.Video.Output(), io.String.Output()]


def live_control() -> io.Input:
    """Declare the switch that opens live controls for the executing client."""
    return io.Boolean.Input(
        "interactive",
        default=False,
    )
