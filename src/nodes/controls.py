"""Build the inputs and outputs that the video nodes share."""

from collections.abc import Sequence

from comfy_api.latest import io

from ..config.nodes import (
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
from ..config.generation.prompts import DEFAULT_PROMPTS


def _shared_controls(
    prompt_key: str, *, duration: io.Input | None, prompt_tooltip: str | None, has_seed: bool
) -> list[io.Input]:
    """List the prompt, duration, seed, and run-number controls that the video nodes share."""
    prompt_label = 'edit prompt' if prompt_key in {'edit', 'webcam'} else 'scene prompt'
    run_tooltip = 'Change this number to run again with unchanged inputs.'
    controls: list[io.Input] = [
        io.String.Input(
            'prompt',
            display_name=prompt_label,
            placeholder=prompt_label,
            tooltip=prompt_tooltip,
            multiline=True,
            default=DEFAULT_PROMPTS[prompt_key],
        ),
        duration
        if duration is not None
        else io.Float.Input(
            'duration_seconds',
            display_name='video duration (seconds)',
            tooltip='Video length in seconds. Setup also counts toward the session time limit.',
            default=DEFAULT_DURATION_SECONDS,
            min=MIN_DURATION_SECONDS,
            max=MAX_DURATION_SECONDS,
            step=STEP_DURATION_SECONDS,
        ),
    ]
    if has_seed:
        run_tooltip += ' This does not change the seed.'
        controls.append(
            io.Int.Input(
                'seed',
                display_name='seed',
                tooltip='Number used by the model to generate the video. Results can change after model updates.',
                default=DEFAULT_SEED,
                min=0,
                max=MAX_SEED,
                control_after_generate=True,
            )
        )
    controls.append(
        io.Int.Input(
            'variation',
            display_name='run number',
            tooltip=run_tooltip,
            default=DEFAULT_VARIATION,
            min=MIN_VARIATION,
            max=MAX_VARIATION,
        )
    )
    return controls


def build_inputs(
    prompt_key: str = 'video',
    *,
    leading: Sequence[io.Input] = (),
    duration: io.Input | None = None,
    trailing: Sequence[io.Input] = (),
    prompt_tooltip: str | None = None,
    has_seed: bool = True,
    is_live: bool = False,
) -> list[io.Input]:
    """List the inputs of a video node in schema order.

    The leading inputs of the node come first. The shared controls follow, then the trailing inputs of the node, and
    last the switch for live controls when the node offers them.
    """
    inputs = [
        *leading,
        *_shared_controls(prompt_key, duration=duration, prompt_tooltip=prompt_tooltip, has_seed=has_seed),
        *trailing,
    ]
    if is_live:
        inputs.append(
            io.Boolean.Input(
                'interactive',
                display_name='live controls',
                tooltip='Open live controls in this ComfyUI window. Start the session there.',
                default=False,
            )
        )
    return inputs


def build_outputs(*, has_audio: bool) -> list[io.Output]:
    """Declare the native video output, and the audio output when the model also returns sound."""
    outputs: list[io.Output] = [io.Video.Output(display_name='video')]
    if has_audio:
        outputs.append(io.Audio.Output(display_name='audio'))
    return outputs
