"""Choose the instructions shown beside each workflow's nodes."""

from .example import Example
from .models.helios import AUTUMN_PROMPT
from .texts import LIVE, SETUP, LIMITS, NODES


def setup_steps(example: Example, model: str) -> list[str]:
    """Write numbered setup actions using the node titles visible in this example."""
    steps = [SETUP["key"]]
    image_key = "portrait" if model == "ltx2" else "image"
    sources = (
        ("source", "video", "sourceVideo"),
        ("image", image_key, "portraitImage" if model == "ltx2" else "startingImage"),
        ("reference_image", "reference", "referenceImage"),
        ("ending_image", "endingImage", "endingImage"),
    )
    steps.extend(SETUP[key].format(title=NODES[title]) for source, key, title in sources if source in example.sources)
    prompt_titles: dict[str, str] = {}
    if example.plan == "shots":
        prompt_key = "shots"
        prompt_titles = {
            "first": NODES["softTransition"] + " (Reactor)",
            "second": NODES["hardCut"] + " (Reactor)",
        }
    elif example.plan == "prompts":
        prompt_key = "sequence"
        prompt_titles = {
            "first": NODES["sunlight"] + " (Reactor)",
            "second": NODES["clearing"] + " (Reactor)",
        }
    elif "image" in example.sources and model.startswith("visko-"):
        prompt_key = "viskoImage"
    elif model == "ltx2":
        prompt_key = "speech"
    elif model in {"sana-streaming", "x2"}:
        prompt_key = "editPrompt"
    else:
        prompt_key = "prompt"
    steps.append(SETUP[prompt_key].format(**prompt_titles))
    steps.append(SETUP["record" if example.mode == "record" else "live"])
    return [f"{number}. {step}" for number, step in enumerate(steps, 1)]


def live_notes(example: Example, model: str) -> list[str]:
    """Explain the example's live start, input, and stop controls."""
    keys: list[str] = []
    if example.mode in {"live", "webcam"}:
        keys.append("camera" if example.mode == "webcam" else "start")
        keys.append("editPrompt" if model in {"sana-streaming", "x2"} else "prompt")
        if model.startswith("visko-"):
            keys.append("sound")
        if model == "x2":
            keys.append("drag")
    elif example.mode != "record":
        keys.append("move")
    if example.mode != "record":
        keys.append("finish")
    notes = [LIVE[key] for key in keys]
    if example.slug == "helios-05-live-prompt":
        notes.insert(2, LIVE["examplePrompt"].format(prompt=AUTUMN_PROMPT))
    return notes


def model_notes(example: Example, model: str) -> list[str]:
    """Explain the model-specific recording and control limits for this example."""
    notes = live_notes(example, model)
    if example.clip_count > 1:
        notes.append(LIMITS["continuation"].format(clips=example.clip_count))
        notes.append(LIMITS["totalDuration"].format(seconds=example.duration_seconds))
    if model == "fast-h3":
        notes.append(LIMITS["fast"])
    if model == "ltx2":
        notes.append(LIMITS["ltx"])
    if "source" in example.sources and example.mode != "record":
        notes.append(LIMITS["sourceVideo"])
    if example.plan == "prompts":
        notes.append(LIMITS["helios"])
    if example.plan == "shots":
        notes.append(LIMITS["longlive"])
    return notes


def sections(example: Example, model: str) -> tuple[str, str]:
    """Separate the short setup note from additional model instructions."""
    setup = "\n".join(setup_steps(example, model))
    notes = model_notes(example, model)
    if "source" in example.sources and example.mode == "record":
        setup += "\n\n" + LIMITS["sourceVideo"]
    return setup, "\n\n".join(notes)
