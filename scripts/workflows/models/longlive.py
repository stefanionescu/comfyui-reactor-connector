"""Describe Longlive workflow inputs and controls."""

from ..example import Example

EXAMPLES = (
    Example(
        "longlive-v2-01-text-to-video",
        "ReactorIncLongLiveGenerate",
        inputs={
            "duration_seconds": 5.0,
            "variation": 0,
            "seed": 42,
            "control_after_generate": "fixed",
            "interactive": False,
        },
    ),
    Example(
        "longlive-v2-02-storyboard",
        "ReactorIncLongLiveStoryboard",
        inputs={
            "duration_seconds": 5.0,
            "variation": 0,
            "seed": 42,
            "control_after_generate": "fixed",
            "storyboard": "[]",
        },
        plan="shots",
    ),
)
