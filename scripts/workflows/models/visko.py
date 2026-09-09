"""Describe Visko workflow inputs and controls."""

from ..example import Example

EXAMPLES = (
    Example(
        "visko-stable-01-text-to-video",
        "ReactorIncViskoStableGenerate",
        inputs={
            "duration_seconds": 5.0,
            "variation": 0,
            "seed": 42,
            "control_after_generate": "fixed",
            "resolution": "",
            "audio_enabled": True,
            "prompt_passthrough": False,
            "interactive": False,
        },
    ),
    Example(
        "visko-stable-02-image-to-video",
        "ReactorIncViskoStableGenerate",
        inputs={
            "duration_seconds": 5.0,
            "variation": 0,
            "seed": 42,
            "control_after_generate": "fixed",
            "resolution": "",
            "audio_enabled": True,
            "prompt_passthrough": True,
            "interactive": False,
        },
        sources=("image",),
    ),
    Example(
        "visko-dynamic-01-text-to-video",
        "ReactorIncViskoDynamicGenerate",
        inputs={
            "duration_seconds": 5.0,
            "variation": 0,
            "seed": 42,
            "control_after_generate": "fixed",
            "resolution": "",
            "audio_enabled": True,
            "prompt_passthrough": False,
            "interactive": False,
        },
    ),
    Example(
        "visko-dynamic-02-image-to-video",
        "ReactorIncViskoDynamicGenerate",
        inputs={
            "duration_seconds": 5.0,
            "variation": 0,
            "seed": 42,
            "control_after_generate": "fixed",
            "resolution": "",
            "audio_enabled": True,
            "prompt_passthrough": True,
            "interactive": False,
        },
        sources=("image",),
    ),
)
