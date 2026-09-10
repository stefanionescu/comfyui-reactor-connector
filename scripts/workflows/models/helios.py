"""Describe Helios workflow inputs and controls."""

from ..example import Example
from ..live import build_live_example

AUTUMN_PROMPT = "The forest leaves turn orange and red as autumn arrives."

SEQUENCE_PROMPTS = {
    "sunlight": "Sunlight reaches the forest floor as the camera moves forward.",
    "clearing": "The camera follows the path into a sunny clearing.",
}

EXAMPLES = (
    Example(
        "helios-01-text-to-video",
        "ReactorIncHeliosGenerate",
        inputs={
            "prompt": "A red ball rolls slowly across a wooden table. The camera stays still.",
            "duration_seconds": 5.0,
            "variation": 0,
            "seed": 42,
            "control_after_generate": "fixed",
            "interactive": False,
        },
    ),
    Example(
        "helios-02-image-to-video",
        "ReactorIncHeliosAnimate",
        inputs={
            "prompt": "The scene comes to life with gentle motion. Keep the subject and composition.",
            "duration_seconds": 5.0,
            "variation": 0,
            "seed": 42,
            "control_after_generate": "fixed",
            "interactive": False,
        },
        sources=("image",),
    ),
)

SEQUENCE_EXAMPLES = tuple(
    Example(
        f"helios-{'04-image-sequence' if image else '03-prompt-sequence'}",
        "ReactorIncHeliosSequence",
        inputs={
            "prompt": "The camera moves slowly along a forest path in soft morning light.",
            "duration_seconds": 8,
            "variation": 0,
            "seed": 42,
            "control_after_generate": "fixed",
            "sequence": "[]",
        },
        sources=("image",) if image else (),
        plan="prompts",
    )
    for image in (False, True)
)


LIVE_EXAMPLES = (
    build_live_example(
        EXAMPLES[0],
        "helios-05-live-prompt",
        prompt="The camera moves slowly along a sunlit forest path. Green leaves sway gently.",
    ),
    build_live_example(EXAMPLES[1], "helios-06-live-image"),
)
