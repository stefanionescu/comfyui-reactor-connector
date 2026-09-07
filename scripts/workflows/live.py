"""Describe webcam, live editing, and continued-scene examples."""

from .example import Example
from dataclasses import replace

LIVE_NODE_IDS = frozenset(
    {
        "ReactorIncHeliosGenerate",
        "ReactorIncHeliosAnimate",
        "ReactorIncLongLiveGenerate",
        "ReactorIncSanaEditVideo",
        "ReactorIncX2EditVideo",
        "ReactorIncViskoStableGenerate",
        "ReactorIncViskoDynamicGenerate",
    }
)


def live_examples(examples: tuple[Example, ...]) -> tuple[Example, ...]:
    """Derive one live-control example per supported node and include the additional camera workflows."""
    selected: dict[str, Example] = {}
    for example in examples:
        if example.node_id in LIVE_NODE_IDS and example.node_id not in selected:
            selected[example.node_id] = example
    slugs = {
        "ReactorIncHeliosGenerate": "helios-05-live-prompt",
        "ReactorIncHeliosAnimate": "helios-06-live-image",
        "ReactorIncLongLiveGenerate": "longlive-v2-03-live-prompt",
        "ReactorIncSanaEditVideo": "sana-streaming-02-live-prompt",
        "ReactorIncX2EditVideo": "x2-04-live-prompt",
        "ReactorIncViskoStableGenerate": "visko-stable-03-live-prompt",
        "ReactorIncViskoDynamicGenerate": "visko-dynamic-03-live-prompt",
    }
    live = tuple(
        replace(
            example,
            slug=slugs[example.node_id],
            title=f"{example.title.split(':')[0]}: "
            + (
                "Drag and edit a video"
                if example.model == "x2"
                else "Animate an image with live prompts"
                if example.image
                else "Change the prompt while recording"
            ),
            duration_seconds=20,
            prompt=(
                "The camera moves slowly along a sunlit forest path. Green leaves sway gently."
                if example.node_id == "ReactorIncHeliosGenerate"
                else example.prompt
            ),
            interactive=True,
            panel=True,
        )
        for example in selected.values()
    )
    return (*live, *ADDITIONAL_EXAMPLES)


ADDITIONAL_EXAMPLES = (
    Example(
        "sana-streaming-03-webcam",
        "SANA: Edit a webcam",
        "ReactorIncSanaWebcam",
        "sana-streaming",
        "Turn the scene into a watercolor painting.",
        controls=(0,),
        duration_seconds=20,
        interactive=True,
        panel=True,
        webcam=True,
    ),
    Example(
        "x2-03-webcam",
        "X2: Edit and drag a webcam scene",
        "ReactorIncX2Webcam",
        "x2",
        "Turn the scene into a watercolor painting.",
        seed=False,
        duration_seconds=20,
        interactive=True,
        panel=True,
        webcam=True,
    ),
    Example(
        "fast-h3-05-continue-scene",
        "Fast H3: Continue a scene",
        "ReactorIncFastContinue",
        "fast-h3",
        "Follow a stream through a quiet forest. Water splashes softly.",
        controls=(
            "16:9",
            3,
            "The stream flows past a mossy rock.\nThe camera follows the stream into a sunlit clearing.",
        ),
        audio=True,
        duration_seconds=18,
        clip_count=3,
    ),
    Example(
        "fast-h3-06-continue-image",
        "Fast H3: Continue from an image",
        "ReactorIncFastContinue",
        "fast-h3",
        "Bring this scene to life with gentle motion and soft natural ambience.",
        controls=("16:9", 3, ""),
        image=True,
        audio=True,
        duration_seconds=18,
        clip_count=3,
    ),
)
