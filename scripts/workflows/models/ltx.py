"""Describe Ltx workflow inputs and controls."""

from ..example import Example

EXAMPLES = (
    Example(
        "ltx2-01-speaking-portrait",
        "ReactorIncLtxSpeak",
        inputs={
            "prompt": "A person faces the camera and speaks calmly.",
            "script": "Hello. Welcome to this short video.",
            "duration_seconds": 5.0,
            "variation": 0,
            "seed": 42,
            "control_after_generate": "fixed",
            "words_per_minute": 140,
        },
        sources=("image",),
    ),
)
