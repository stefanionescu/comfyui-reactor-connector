"""Shared controls for video generation."""

from comfy_api.latest import io


def generation_controls(
    prompt: str = "A red ball rolls across a wooden table.",
) -> list[io.Input]:
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
            default=5.0,
            min=0.1,
            max=60.0,
            step=0.1,
            tooltip="Video length in seconds. Setup also counts toward the session time limit.",
        ),
        io.Int.Input(
            "seed",
            display_name="Seed",
            default=42,
            min=0,
            max=2**32 - 1,
            control_after_generate=True,
            tooltip=(
                "Number used by the model to generate the video. "
                "Results can change after model updates."
            ),
        ),
        io.Int.Input(
            "variation",
            display_name="Variation",
            default=0,
            min=0,
            max=2**31 - 1,
            tooltip="Change this value to request a new paid run with the same prompt and seed.",
        ),
    ]


def video_outputs() -> list[io.Output]:
    return [io.Video.Output(display_name="video"), io.String.Output(display_name="metadata")]


def live_control() -> io.Input:
    return io.Boolean.Input(
        "interactive",
        display_name="Live controls",
        default=False,
        tooltip="Open live controls in this ComfyUI window. Start the session there.",
    )
