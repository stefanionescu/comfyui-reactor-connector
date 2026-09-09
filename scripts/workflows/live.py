"""Derive live prompt examples from each model family."""

from .example import Example
from dataclasses import replace


def live_examples(examples: tuple[Example, ...]) -> tuple[Example, ...]:
    """Derive one live-control example per supported node from its recorded example."""
    slugs = {
        "ReactorIncHeliosGenerate": "helios-05-live-prompt",
        "ReactorIncHeliosAnimate": "helios-06-live-image",
        "ReactorIncLongLiveGenerate": "longlive-v2-03-live-prompt",
        "ReactorIncSanaEditVideo": "sana-streaming-02-live-prompt",
        "ReactorIncX2EditVideo": "x2-04-live-prompt",
        "ReactorIncViskoStableGenerate": "visko-stable-03-live-prompt",
        "ReactorIncViskoDynamicGenerate": "visko-dynamic-03-live-prompt",
    }
    selected: dict[str, Example] = {}
    for example in examples:
        if example.node_id in slugs and example.node_id not in selected:
            selected[example.node_id] = example
    return tuple(
        replace(
            example,
            slug=slugs[example.node_id],
            inputs=example.inputs
            | {
                "duration_seconds": 20,
                "interactive": True,
            },
            mode="live",
        )
        for example in selected.values()
    )
