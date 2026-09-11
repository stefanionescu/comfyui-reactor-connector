"""Describe Visko workflow inputs and controls."""

from ..example import Example
from ..live import build_live_example

RECORDING_INPUTS: dict[str, str | float | bool] = {
    "duration_seconds": 5.0,
    "variation": 0,
    "seed": 42,
    "control_after_generate": "fixed",
    "resolution": "",
    "audio_enabled": True,
    "interactive": False,
}
TEXT_INPUTS = RECORDING_INPUTS | {
    "audio_prompt": "Water splashes softly over stones, with birds calling in the distance.",
    "prompt": "A small stream flows over smooth stones in a quiet forest.",
    "prompt_passthrough": False,
}
IMAGE_INPUTS = RECORDING_INPUTS | {
    "audio_prompt": "",
    "prompt": (
        "The camera moves slowly along a forest path. Ferns and leaves sway gently. Keep "
        "the trees, path, and lighting from the starting image."
    ),
    "prompt_passthrough": True,
}

EXAMPLES = (
    Example(
        "visko-stable-01-text-to-video",
        "ReactorIncViskoStableGenerate",
        inputs=TEXT_INPUTS,
    ),
    Example(
        "visko-stable-02-image-to-video",
        "ReactorIncViskoStableGenerate",
        inputs=IMAGE_INPUTS,
        sources=("image",),
    ),
    Example(
        "visko-dynamic-01-text-to-video",
        "ReactorIncViskoDynamicGenerate",
        inputs=TEXT_INPUTS,
    ),
    Example(
        "visko-dynamic-02-image-to-video",
        "ReactorIncViskoDynamicGenerate",
        inputs=IMAGE_INPUTS,
        sources=("image",),
    ),
)


LIVE_EXAMPLES = (
    build_live_example(EXAMPLES[0], "visko-stable-03-live-prompt"),
    build_live_example(EXAMPLES[2], "visko-dynamic-03-live-prompt"),
)
