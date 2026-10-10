"""Describe Fast workflow inputs and controls."""

from ..example import Example

EXAMPLES = (
    Example(
        "fast-h3-03-first-and-last-frames",
        "ReactorIncFastGenerate",
        model="fast-h3",
        inputs={
            "prompt": "Move smoothly from the first scene to the final scene. Keep the motion natural. Soft ambience.",
            "duration_seconds": 6.0,
            "variation": 0,
            "seed": 42,
            "control_after_generate": "fixed",
            "aspect": "16:9",
        },
        sources=("image", "ending_image"),
    ),
    Example(
        "fast-h3-01-text-to-video",
        "ReactorIncFastGenerate",
        model="fast-h3",
        inputs={
            "prompt": "A small stream flows over smooth stones. Water splashes softly and birds call.",
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
        model="fast-h3",
        inputs={
            "prompt": (
                "Bring this scene to life with gentle motion. Keep the subject and composition. Soft natural ambience."
            ),
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
        model="fast-h3",
        inputs={
            "later_prompts": (
                "The stream flows past a mossy rock.\nThe camera follows the stream into a sunlit clearing."
            ),
            "prompt": "Follow a stream through a quiet forest. Water splashes softly.",
            "variation": 0,
            "seed": 42,
            "control_after_generate": "fixed",
            "clip_seconds": 6.0,
            "aspect": "16:9",
            "clip_count": 3,
        },
    ),
)
