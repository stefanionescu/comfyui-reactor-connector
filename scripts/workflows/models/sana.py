"""Describe Sana workflow inputs and controls."""

from ..example import Example
from ..live import build_live_example

EXAMPLES = (
    Example(
        "sana-streaming-01-edit-video",
        "ReactorIncSanaEditVideo",
        inputs={
            "prompt": "Change the scene to a soft watercolor painting. Keep the movement and composition.",
            "duration_seconds": 5.0,
            "variation": 0,
            "seed": 42,
            "control_after_generate": "fixed",
            "anchor_interval": 0,
            "interactive": False,
        },
        sources=("source",),
    ),
    Example(
        "sana-streaming-03-webcam",
        "ReactorIncSanaWebcam",
        inputs={
            "prompt": "Turn the scene into a watercolor painting.",
            "duration_seconds": 20,
            "variation": 0,
            "seed": 42,
            "control_after_generate": "fixed",
            "anchor_interval": 0,
        },
        mode="webcam",
    ),
)


LIVE_EXAMPLES = (build_live_example(EXAMPLES[0], "sana-streaming-02-live-prompt"),)
