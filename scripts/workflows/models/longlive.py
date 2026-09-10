"""Describe Longlive workflow inputs and controls."""

from ..example import Example
from ..live import build_live_example

SHOT_PROMPTS = {
    "soft_transition": "The camera pulls back to show the trees around the fox.",
    "hard_cut": "A wide view of a still lake at sunrise.",
}

EXAMPLES = (
    Example(
        "longlive-v2-01-text-to-video",
        "ReactorIncLongLiveGenerate",
        inputs={
            "prompt": "A fox walks along a forest path. The camera follows slowly.",
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
            "prompt": "A fox walks along a forest path. The camera follows slowly.",
            "duration_seconds": 5.0,
            "variation": 0,
            "seed": 42,
            "control_after_generate": "fixed",
            "storyboard": "[]",
        },
        plan="shots",
    ),
)


LIVE_EXAMPLES = (build_live_example(EXAMPLES[0], "longlive-v2-03-live-prompt"),)
