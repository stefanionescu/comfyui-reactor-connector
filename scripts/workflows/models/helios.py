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
        model="helios",
        inputs={
            "prompt": "A red ball rolls slowly across a wooden table. The camera stays still.",
            "duration_seconds": 5.0,
            "variation": 0,
            "seed": 42,
            "control_after_generate": "fixed",
            "sequence": "[]",
            "interactive": False,
        },
    ),
    Example(
        "helios-02-image-to-video",
        "ReactorIncHeliosGenerate",
        model="helios",
        inputs={
            "prompt": "The scene comes to life with gentle motion. Keep the subject and composition.",
            "duration_seconds": 5.0,
            "variation": 0,
            "seed": 42,
            "control_after_generate": "fixed",
            "sequence": "[]",
            "interactive": False,
        },
        sources=("image",),
    ),
)

SEQUENCE_EXAMPLES = (
    Example(
        "helios-03-prompt-sequence",
        "ReactorIncHeliosGenerate",
        model="helios",
        inputs={
            "prompt": "The camera moves slowly along a forest path in soft morning light.",
            "duration_seconds": 8,
            "variation": 0,
            "seed": 42,
            "control_after_generate": "fixed",
            "sequence": "[]",
            "interactive": False,
        },
        plan="prompts",
    ),
)


LIVE_EXAMPLES = (
    build_live_example(
        EXAMPLES[0],
        "helios-05-live-prompt",
        prompt="The camera moves slowly along a sunlit forest path. Green leaves sway gently.",
    ),
)
