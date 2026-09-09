"""Choose the instructions shown beside each workflow's nodes."""

from .example import Example
from ...src.language import translate


def setup_steps(example: Example) -> list[str]:
    """Write numbered setup actions using the node titles visible in this example."""
    steps = [translate("workflows", "setup.key")]
    image_key = "setup.portrait" if example.model == "ltx2" else "setup.image"
    sources = (
        ("source", "setup.video"),
        ("image", image_key),
        ("reference_image", "setup.reference"),
        ("ending_image", "setup.endingImage"),
    )
    steps.extend(translate("workflows", key) for source, key in sources if source in example.sources)
    if example.plan == "shots":
        prompt_key = "setup.shots"
    elif example.plan == "prompts":
        prompt_key = "setup.sequence"
    elif "image" in example.sources and example.model.startswith("visko-"):
        prompt_key = "setup.viskoImage"
    elif example.model == "ltx2":
        prompt_key = "setup.speech"
    elif example.model in {"sana-streaming", "x2"}:
        prompt_key = "setup.editPrompt"
    else:
        prompt_key = "setup.prompt"
    steps.append(translate("workflows", prompt_key))
    steps.append(translate("workflows", "setup.record" if example.mode == "record" else "setup.live"))
    return [f"{number}. {step}" for number, step in enumerate(steps, 1)]


def live_notes(example: Example) -> list[str]:
    """Explain the example's live start, input, and stop controls."""
    keys: list[str] = []
    if example.mode in {"live", "webcam"}:
        keys.append("live.camera" if example.mode == "webcam" else "live.start")
        keys.append("live.editPrompt" if example.model in {"sana-streaming", "x2"} else "live.prompt")
        if example.slug == "helios-05-live-prompt":
            keys.append("live.autumn")
        if example.model.startswith("visko-"):
            keys.append("live.sound")
        if example.model == "x2":
            keys.append("live.drag")
    elif example.mode != "record":
        keys.append("live.move")
    if example.mode != "record":
        keys.append("live.finish")
    return [translate("workflows", key) for key in keys]


def model_notes(example: Example) -> list[str]:
    """Explain the model-specific recording and control limits for this example."""
    notes = live_notes(example)
    if example.clip_count > 1:
        notes.append(translate("workflows", "limits.continuation", clips=example.clip_count))
        notes.append(translate("workflows", "limits.totalDuration", seconds=example.duration_seconds))
    if example.model == "fast-h3":
        notes.append(translate("workflows", "limits.fast"))
    if example.model == "ltx2":
        notes.append(translate("workflows", "limits.ltx"))
    if "source" in example.sources:
        notes.append(translate("workflows", "limits.sourceVideo"))
    if example.plan == "prompts":
        notes.append(translate("workflows", "limits.helios"))
    if example.plan == "shots":
        notes.append(translate("workflows", "limits.longlive"))
    return notes


def sections(example: Example) -> tuple[str, str]:
    """Separate the short setup note from additional model instructions."""
    setup = "\n".join(setup_steps(example))
    notes = model_notes(example)
    if "source" in example.sources and example.mode == "record":
        setup += "\n\n" + notes.pop()
    return setup, "\n\n".join(notes)
