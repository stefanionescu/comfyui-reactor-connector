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


def generation_controls(prompt_key: str = "video") -> list[io.Input]:
    """Build the shared prompt, duration, seed, and repeat-run controls."""
    prompt_label = "Edit prompt" if prompt_key in {"edit", "webcam"} else "Scene prompt"
    return [
        io.String.Input(
            "prompt",
            display_name=prompt_label,
            placeholder=prompt_label,
            multiline=True,
            default=DEFAULT_PROMPTS[prompt_key],
        ),
        io.Float.Input(
            "duration_seconds",
            display_name="Video length (seconds)",
            tooltip="Video length in seconds. Setup also counts toward the session time limit.",
            default=DEFAULT_DURATION_SECONDS,
            min=MIN_DURATION_SECONDS,
            max=MAX_DURATION_SECONDS,
            step=STEP_DURATION_SECONDS,
        ),
        io.Int.Input(
            "seed",
            display_name="Seed",
            tooltip="Number used by the model to generate the video. Results can change after model updates.",
            default=DEFAULT_SEED,
            min=0,
            max=MAX_SEED,
            control_after_generate=True,
        ),
        io.Int.Input(
            "variation",
            display_name="Run number",
            tooltip="Change this number to run again with unchanged inputs. This does not change the seed.",
            default=DEFAULT_VARIATION,
            min=MIN_VARIATION,
            max=MAX_VARIATION,
        ),
    ]


def video_outputs() -> list[io.Output]:
    """Declare the native video and recording-details output sockets."""
    return [io.Video.Output(display_name="Video"), io.String.Output(display_name="Recording details")]


def live_control() -> io.Input:
    """Declare the switch that opens live controls for the executing client."""
    return io.Boolean.Input(
        "interactive",
        display_name="Live controls",
        tooltip="Open live controls in this ComfyUI window. Start the session there.",
        default=False,
    )
