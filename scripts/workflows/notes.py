"""Write the steps needed to use each example on the canvas."""

from .example import Example


def setup_steps(example: Example) -> list[str]:
    """Write numbered setup actions using the node titles visible in this example."""
    steps = ["Set your key in **ComfyUI menu → Extensions → Reactor → Reactor settings**."]
    subject = "a portrait" if example.model == "ltx2" else "an image"
    sources = (
        (example.video, "Upload a video in **Upload your source video** (at least 33 frames)."),
        (example.image, f"Upload {subject} in **Upload your starting image**."),
        (example.reference, "Upload the subject to insert in **Upload your reference subject**."),
        (example.ending_image, "Upload the ending image in **Choose the final frame**."),
    )
    steps.extend(instruction for needed, instruction in sources if needed)
    if example.storyboard:
        steps.append("Edit the opening prompt, **1. Soft transition**, and **2. Hard cut**.")
    elif example.prompt_sequence:
        steps.append("Edit the opening prompt, **1. Let sunlight through**, and **2. Enter a clearing**.")
    elif example.image and example.model.startswith("visko-"):
        steps.append(
            "Edit **Scene prompt** to name what is in your image and describe its motion. "
            "The example prompt describes a forest path."
        )
    elif example.model == "ltx2":
        steps.append("Edit **Spoken words**. Keep the speech short enough for five seconds.")
    else:
        steps.append("Edit **Scene prompt** to describe the scene or change you want.")
    if example.interactive:
        steps.append("Select **Run** to open the live panel.")
    else:
        steps.append("Select **Run** to create and save the video.")
    return [f"{number}. {step}" for number, step in enumerate(steps, 1)]


def live_notes(example: Example) -> list[str]:
    """Explain the example's live start, input, and stop controls."""
    notes: list[str] = []
    if example.panel:
        if example.webcam:
            notes.append(
                "Select **Enable camera**, allow access, then **Start session**. "
                "Reactor receives camera video without microphone audio."
            )
        else:
            notes.append("In the live panel, select **Start session** within 60 seconds.")
        notes.append("Edit **Scene prompt**, then select **Apply prompt** to change later frames.")
        if example.slug == "helios-05-live-prompt":
            notes.append("Try: The forest leaves turn orange and red as autumn arrives.")
        if example.model.startswith("visko-"):
            notes.append("**Apply sound prompt** changes later sound. The live preview is silent.")
        if example.model == "x2":
            notes.append(
                "Drag on the output to steer the subject. Escape releases the pointer. "
                "**Help** also explains keyboard controls."
            )
    elif example.interactive:
        notes.append(
            "In the live panel, click the picture. W A S D moves; arrow keys turn. "
            "Escape stops movement. **Apply prompt** changes later frames."
        )
    if example.interactive:
        notes.append("Let recording finish to save the video. **End session** stops early and discards it.")
    return notes


def model_notes(example: Example) -> list[str]:
    """Explain the model-specific recording, control, and credit limits for this example."""
    notes = live_notes(example)
    if example.clip_count > 1:
        notes.append(
            f"The {example.clip_count} clips continue from each previous final frame. "
            "Put one prompt per line in **Later prompts**, starting with clip 2. "
            "Leave it empty to repeat the opening prompt."
        )
        notes.append(
            f"This example requests {example.duration_seconds:g} seconds "
            "in total. In Reactor settings, **Maximum video duration (seconds)** must allow "
            "the combined length. The model may round each clip up."
        )
    if example.model == "fast-h3":
        notes.append(
            "Fast H3 rounds each clip to a supported length. It also generates up to "
            "14.375 extra seconds for recording to finish. Those extra seconds use "
            "credits but are not saved."
        )
    if example.model == "ltx2":
        notes.append(
            "Use a clear portrait with the whole head visible. LTX may generate up to "
            "20 extra seconds while recording starts; those seconds can use credits "
            "but are not saved."
        )
    if example.video:
        notes.append("Use standard dynamic range (SDR) video. The edited output has no sound.")
    if example.prompt_sequence:
        notes.append(
            "Each Helios chunk contains 33 frames. Connect prompts in order and use "
            "increasing **Start chunk** values. The opening prompt starts at chunk 0. "
            "Later prompts do not extend the recording."
        )
    if example.storyboard:
        notes.append(
            "Each LongLive chunk is about 1.2 seconds at 24 fps. The soft transition "
            "starts near 1.2 seconds; the hard cut near 2.4 seconds. Increase "
            "**Video length (seconds)** if you schedule later shots."
        )
    return notes


def sections(example: Example) -> tuple[str, str]:
    """Separate the short setup note from additional model instructions."""
    setup = "\n".join(setup_steps(example))
    notes = model_notes(example)
    if example.video and not example.interactive:
        setup += "\n\n" + notes.pop()
    setup += "\n\nRun uses Reactor credits. Select a Reactor node, then choose **Help** for costs and limits."
    return setup, "\n\n".join(notes)
