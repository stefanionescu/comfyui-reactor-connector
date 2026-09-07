"""Shared controls for video generation."""

from comfy_api.latest import io
from ...config.prompts import VIDEO_CONTROLS_PROMPT
from ...config.nodes import (
    MAX_SEED,
    DEFAULT_SEED,
    MAX_VARIATION,
    MAX_DURATION_SECONDS,
    MIN_DURATION_SECONDS,
    STEP_DURATION_SECONDS,
    DEFAULT_DURATION_SECONDS,
)


def generation_controls(
    prompt: str = VIDEO_CONTROLS_PROMPT,
) -> list[io.Input]:
    """Build the shared prompt, duration, seed, and repeat-run controls."""
    return [
        io.String.Input(
            "prompt",
            display_name="Scene prompt",
            placeholder="Scene prompt",
            multiline=True,
            default=prompt,
        ),
        io.Float.Input(
            "duration_seconds",
            display_name="Video length (seconds)",
            default=DEFAULT_DURATION_SECONDS,
            min=MIN_DURATION_SECONDS,
            max=MAX_DURATION_SECONDS,
            step=STEP_DURATION_SECONDS,
            tooltip="Video length in seconds. Setup also counts toward the session time limit.",
        ),
        io.Int.Input(
            "seed",
            display_name="Seed",
            default=DEFAULT_SEED,
            min=0,
            max=MAX_SEED,
            control_after_generate=True,
            tooltip=("Number used by the model to generate the video. Results can change after model updates."),
        ),
        io.Int.Input(
            "variation",
            display_name="Variation",
            default=0,
            min=0,
            max=MAX_VARIATION,
            tooltip="Change this value to request a new paid run with the same prompt and seed.",
        ),
    ]


def video_outputs() -> list[io.Output]:
    """Declare the native video and recording-details output sockets."""
    return [io.Video.Output(display_name="video"), io.String.Output(display_name="metadata")]


def live_control() -> io.Input:
    """Declare the switch that opens live controls for the executing client."""
    return io.Boolean.Input(
        "interactive",
        display_name="Live controls",
        default=False,
        tooltip="Open live controls in this ComfyUI window. Start the session there.",
    )
