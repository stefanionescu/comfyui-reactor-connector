"""Describe Sana workflow inputs and controls."""

from ..example import Example

EXAMPLES = (
    Example(
        "sana-streaming-01-edit-video",
        "ReactorIncSanaEditVideo",
        inputs={
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
            "duration_seconds": 20,
            "variation": 0,
            "seed": 42,
            "control_after_generate": "fixed",
            "anchor_interval": 0,
        },
        mode="webcam",
    ),
)
