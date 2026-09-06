"""List every built workflow so new examples cannot disappear from the index."""

from .workflow_definitions import EXAMPLES, Example

GUIDES = {
    "fast-h3": ("Fast H3", "fast-h3"),
    "helios": ("Helios", "helios"),
    "lingbot": ("LingBot", "lingbot"),
    "lingbot-world-2": ("LingBot World 2", "lingbot"),
    "longlive-v2": ("LongLive", "longlive"),
    "ltx2": ("LTX", "ltx"),
    "sana-streaming": ("SANA", "sana"),
    "visko-orbis-dynamic": ("Visko Dynamic", "visko"),
    "visko-orbis-stable": ("Visko Stable", "visko"),
    "x2": ("X2", "x2"),
}


def input_summary(example: Example) -> str:
    if example.webcam:
        return "Webcam and live edit prompt"
    if example.clip_count > 1:
        return (
            "Starting image and continued clips" if example.image else "Prompts for continued clips"
        )
    if example.panel:
        return (
            "Source video and live controls"
            if example.video
            else "Image and live prompt"
            if example.image
            else "Live prompt"
        )
    if example.model == "ltx2":
        return "Portrait and speech script"
    if example.storyboard:
        return "Opening prompt and two scheduled shots"
    if example.prompt_sequence:
        return "Starting image and scheduled prompts" if example.image else "Scheduled prompts"
    if example.video:
        return (
            "Video, edit prompt, and reference image"
            if example.reference
            else "Video and edit prompt"
        )
    if example.image and example.ending_image:
        return "First image, final image, and prompt"
    if example.ending_image:
        return "Final image and prompt"
    if example.image:
        return (
            "Image and prompt; live keys or buttons" if example.interactive else "Image and prompt"
        )
    return "Scene and sound prompt" if example.audio else "Scene prompt"


def workflow_index() -> str:
    lines = [
        "# Reactor workflows",
        "",
        f"This folder contains {len(EXAMPLES)} editable ComfyUI workflows. "
        "Examples are grouped in model folders. Each JSON file opens as a graph "
        "with connected nodes, a short setup note, and extra instructions where needed.",
        "",
        "## Open a workflow",
        "",
        "1. Download or locate a JSON file listed below.",
        "2. Drag it onto the ComfyUI canvas. You can also open **Templates**, "
        "choose **reactor-inc**, and select the same example.",
        "3. Read **Start here**. Upload your own image or video when the example needs one.",
        "4. Set your key privately in **ComfyUI menu → Extensions → Reactor → Reactor settings**. "
        "Select **Run** when the inputs are ready.",
        "",
        "Opening a workflow does not start generation. A new generation uses Reactor credits.",
        "Use the [sample inputs](assets/README.md) if you need an image or short source clip.",
        "",
        "## Open the latest example after an update",
        "",
        "Updating Reactor does not replace graphs already open in ComfyUI. Save your own "
        "changes, create a new workflow tab, and open the example again from **Templates**. "
        "Keep the old tab until you have copied any prompts or settings you want to reuse.",
        "",
        "## Available files",
        "",
        "| Model | Workflow JSON | Input | Guide |",
        "| --- | --- | --- | --- |",
    ]
    for example in sorted(EXAMPLES, key=lambda item: item.slug):
        name, guide = GUIDES[example.model]
        lines.append(
            f"| {name} | [{example.title.split(': ', 1)[-1]}]({example.path}) | "
            f"{input_summary(example)} | [Steps](../docs/workflows/{guide}.md) |"
        )
    lines.extend(
        [
            "",
            "## Save, stop, and get help",
            "",
            "**Preview and save video** previews the result and writes to `video/reactor/` under "
            "the ComfyUI output folder. Examples with sound also save a separate audio file.",
            "",
            "Use ComfyUI's cancel control to stop a run. Closing a tab does not cancel "
            "an ordinary queued graph. In a live-camera panel, **End session** stops "
            "the session and discards the unfinished video.",
            "",
            "Select a Reactor node, then choose **Help** for its inputs, limits, and recovery "
            "steps. Use **Fit View** to find all nodes, then zoom in to read or edit them.",
            "",
            "## Current limits",
            "",
            "These examples use native ComfyUI nodes and Reactor. "
            "Media inputs start empty; the graphs "
            "contain no private files, machine-specific paths, or API keys.",
            "",
            "Live workflows stop at the chosen duration. Fast H3 can chain a chosen "
            "number of clips; the node guide explains recording length and credit use.",
            "",
        ]
    )
    return "\n".join(lines)
