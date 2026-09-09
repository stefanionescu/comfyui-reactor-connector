"""Describe Helios workflow inputs and controls."""

from ..example import Example

EXAMPLES = (
    Example(
        "helios-01-text-to-video",
        "ReactorIncHeliosGenerate",
        inputs={
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
