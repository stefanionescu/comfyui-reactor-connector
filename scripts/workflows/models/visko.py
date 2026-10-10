"""Describe Visko workflow inputs and controls."""

from ..example import Example
from ..live import build_live_example

RECORDING_INPUTS: dict[str, str | float | bool] = {
    "model": "stable",
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
        "visko-01-text-to-video",
        "ReactorIncViskoGenerate",
        model="visko-orbis-stable",
        inputs=TEXT_INPUTS,
    ),
    Example(
        "visko-02-image-to-video",
        "ReactorIncViskoGenerate",
        model="visko-orbis-stable",
        inputs=IMAGE_INPUTS,
        sources=("image",),
    ),
)


LIVE_EXAMPLES = (build_live_example(EXAMPLES[0], "visko-03-live-prompt"),)
