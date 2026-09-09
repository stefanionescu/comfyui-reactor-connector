"""Describe X2 workflow inputs and controls."""

from ..example import Example

EXAMPLES = (
    Example(
        "x2-01-edit-video",
        "ReactorIncX2EditVideo",
        inputs={
            "duration_seconds": 5.0,
            "variation": 0,
            "keep_backlog": False,
            "pointer_active": False,
            "pointer_x": 0.5,
            "pointer_y": 0.5,
            "interactive": False,
        },
        sources=("source",),
    ),
    Example(
        "x2-02-reference-edit",
        "ReactorIncX2EditVideo",
        inputs={
            "duration_seconds": 5.0,
            "variation": 0,
            "keep_backlog": False,
            "pointer_active": False,
            "pointer_x": 0.5,
            "pointer_y": 0.5,
            "interactive": False,
        },
        sources=("source", "reference_image"),
    ),
    Example(
        "x2-03-webcam",
        "ReactorIncX2Webcam",
        inputs={"duration_seconds": 20, "variation": 0},
        mode="webcam",
    ),
)
