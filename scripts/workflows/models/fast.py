"""Describe Fast workflow inputs and controls."""

from ..example import Example

EXAMPLES = (
    Example(
        "fast-h3-03-first-and-last-frames",
        "ReactorIncFastGenerate",
        inputs={
            "duration_seconds": 6.0,
            "variation": 0,
            "seed": 42,
            "control_after_generate": "fixed",
            "aspect": "16:9",
        },
        sources=("image", "ending_image"),
    ),
    Example(
        "fast-h3-04-ending-frame",
        "ReactorIncFastGenerate",
        inputs={
            "duration_seconds": 6.0,
            "variation": 0,
            "seed": 42,
            "control_after_generate": "fixed",
            "aspect": "16:9",
        },
        sources=("ending_image",),
    ),
    Example(
        "fast-h3-01-text-to-video",
        "ReactorIncFastGenerate",
        inputs={
            "duration_seconds": 6.0,
            "variation": 0,
            "seed": 42,
            "control_after_generate": "fixed",
            "aspect": "16:9",
        },
    ),
    Example(
        "fast-h3-02-image-to-video",
        "ReactorIncFastGenerate",
        inputs={
            "duration_seconds": 6.0,
            "variation": 0,
            "seed": 42,
            "control_after_generate": "fixed",
            "aspect": "16:9",
        },
        sources=("image",),
    ),
    Example(
        "fast-h3-05-continue-scene",
        "ReactorIncFastContinue",
        inputs={
            "variation": 0,
            "seed": 42,
            "control_after_generate": "fixed",
            "clip_seconds": 6.0,
            "aspect": "16:9",
            "clip_count": 3,
        },
    ),
    Example(
        "fast-h3-06-continue-image",
        "ReactorIncFastContinue",
        inputs={
            "variation": 0,
            "seed": 42,
            "control_after_generate": "fixed",
            "clip_seconds": 6.0,
            "aspect": "16:9",
            "clip_count": 3,
        },
        sources=("image",),
    ),
)
