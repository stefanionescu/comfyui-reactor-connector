"""List every built workflow so new examples cannot disappear from the index."""

from .example import Example
from .definitions import EXAMPLES
from .serialize import output_types
from ...src.serialization import Json

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


def input_summary(example: Example, schema: Json) -> str:
    """Describe the inputs and controls needed by one workflow."""
    choices = (
        ((example.mode == "webcam"), "Webcam and live edit prompt"),
        (
            example.clip_count > 1,
            "Starting image and continued clips" if ("image" in example.sources) else "Prompts for continued clips",
        ),
        (
            (example.mode in {"live", "webcam"}),
            "Source video and live controls"
            if ("source" in example.sources)
            else "Image and live prompt"
            if ("image" in example.sources)
            else "Live prompt",
        ),
        (example.model == "ltx2", "Portrait and speech script"),
        ((example.plan == "shots"), "Opening prompt and two scheduled shots"),
        (
            (example.plan == "prompts"),
            "Starting image and scheduled prompts" if ("image" in example.sources) else "Scheduled prompts",
        ),
        (
            ("source" in example.sources),
            "Video, edit prompt, and reference image"
            if ("reference_image" in example.sources)
            else "Video and edit prompt",
        ),
        (("image" in example.sources) and ("ending_image" in example.sources), "First image, final image, and prompt"),
        (("ending_image" in example.sources), "Final image and prompt"),
        (
            ("image" in example.sources),
            "Image and prompt; live keys or buttons" if (example.mode != "record") else "Image and prompt",
        ),
    )
    return next(
        (text for applies, text in choices if applies),
        "Scene and sound prompt" if ("AUDIO" in output_types(schema)) else "Scene prompt",
    )


def workflow_rows(schemas: dict[str, Json]) -> list[str]:
    """List each graph with the node guide for its operation."""
    lines: list[str] = []
    for example in sorted(EXAMPLES, key=lambda item: item.slug):
        name, _ = GUIDES[example.model]
        lines.append(
            f"| {name} | [{example.title.split(': ', 1)[-1]}]({example.path}) | "
            f"{input_summary(example, schemas[example.node_id])} | [Node guide](../web/docs/{example.node_id}.md) |"
        )
    return lines


USAGE_NOTES = [
    "",
    "## Save, stop, and get help",
    "",
    (
        "**Preview and save video** previews the result and writes to `video/reactor/` under "
        "the ComfyUI output folder. Examples with sound also save a separate audio file."
    ),
    "",
    (
        "Use ComfyUI's cancel control to stop a run. Closing a tab does not cancel "
        "an ordinary queued graph. In a live-camera panel, **End session** stops "
        "the session and discards the unfinished video."
    ),
    "",
    (
        "Select a Reactor node, then choose **Help** for its inputs, limits, and recovery "
        "steps. Use **Fit View** to find all nodes, then zoom in to read or edit them."
    ),
    "",
    "## Current limits",
    "",
    (
        "These examples use native ComfyUI nodes and Reactor. "
        "Media inputs start empty; the graphs "
        "contain no private files, machine-specific paths, or API keys."
    ),
    "",
    (
        "Live workflows stop at the chosen duration. Fast H3 can chain a chosen "
        "number of clips; the node guide explains recording length and credit use."
    ),
    "",
]


def workflow_index(schemas: dict[str, Json]) -> str:
    """Render the workflow index with setup, saving, limits, and sample inputs."""
    lines = [
        "# Reactor Workflows",
        "",
        (
            f"This folder contains {len(EXAMPLES)} editable ComfyUI workflows. "
            "Examples are grouped in model folders. Each JSON file opens as a graph "
            "with connected nodes, a short setup note, and extra instructions where needed."
        ),
        "",
        "## Open a workflow",
        "",
        "1. Download or locate a JSON file listed below.",
        (
            "2. Drag it onto the ComfyUI canvas. You can also open **Templates**, "
            "choose **reactor-inc**, and select the same example."
        ),
        "3. Read **Start here**. Upload your own image or video when the example needs one.",
        (
            "4. Set your key privately in **ComfyUI menu → Extensions → Reactor → Reactor settings**. "
            "Select **Run** when the inputs are ready."
        ),
        "",
        "Opening a workflow does not start generation. A new generation uses Reactor credits.",
        "Use the [sample inputs](#sample-inputs) if you need an image or short source clip.",
        "",
        "## Open the latest example after an update",
        "",
        (
            "Updating Reactor does not replace graphs already open in ComfyUI. Save your own "
            "changes, create a new workflow tab, and open the example again from **Templates**. "
            "Keep the old tab until you have copied any prompts or settings you want to reuse."
        ),
        "",
        "## Available files",
        "",
        "| Model | Workflow JSON | Input | Guide |",
        "| --- | --- | --- | --- |",
    ]
    lines.extend(workflow_rows(schemas))
    lines.extend(USAGE_NOTES)
    return "\n".join(lines) + "\n" + SAMPLE_INPUTS


SAMPLE_INPUTS = (
    "## Sample inputs\n"
    "\n"
    "Download an image below, then choose it in the workflow's image upload node.\n"
    "You can use your own files instead. Uploading a sample to ComfyUI is free;\n"
    "running a Reactor generation uses your Reactor credits.\n"
    "\n"
    "| File | Use it for |\n"
    "| --- | --- |\n"
    "| [Forest path](assets/forest-path.png) | Animate an image, move through a scene, or "
    "continue a clip. |\n"
    "| [Forest illustration](assets/forest-illustration.png) | Animate a landscape "
    "illustration or use it as a reference image. |\n"
    "| [Fictional portrait](assets/fictional-portrait.png) | Make a portrait speak with "
    "LTX. |\n"
    "| [Forest motion](assets/forest-motion.mp4) | Edit a five-second clip with SANA or "
    "X2. |\n"
    "\n"
    "The images have a wide frame. The portrait depicts a fictional adult, not an\n"
    "identified person. Both forest images show invented scenes.\n"
    "\n"
    "Use either forest image in workflows that accept a starting image.\n"
    "\n"
    "### Origin and reuse\n"
    "\n"
    "These images were generated for this project using OpenAI's built-in image\n"
    "generation tool. They use no supplied photograph or third-party reference image.\n"
    "Project rights in these sample assets are licensed under\n"
    "[MIT](../LICENSE.md). The samples are inputs, not examples of Reactor output.\n"
    "\n"
    "The video adds a slow zoom to the forest image. It contains 120 frames at 24 fps,\n"
    "uses 640 by 360 pixels in standard dynamic range, and has no sound. It was made\n"
    "with FFmpeg from the included forest image and uses the same license.\n"
    "\n"
    "### Workflow previews\n"
    "\n"
    "These previews show a frame from each workflow's Reactor output:\n"
    "\n"
    "| Preview | Workflow |\n"
    "| --- | --- |\n"
    "| [Stream over rocks](fast-h3/fast-h3-01-text-to-video.jpg) | [Fast H3: Build a clip "
    "with sound](fast-h3/fast-h3-01-text-to-video.json) |\n"
    "| [Animated forest](helios/helios-02-image-to-video.jpg) | [Helios: Animate a local "
    "image](helios/helios-02-image-to-video.json) |\n"
    "\n"
    "These previews use the example prompts and, for Helios, the forest illustration\n"
    "above. Your output can differ. Project rights in these preview images use the\n"
    "same MIT license as the sample inputs.\n"
)
