"""List every built workflow so new examples cannot disappear from the index."""

from .example import Example
from ...src.models import MODELS
from .definitions import EXAMPLES
from .serialize import output_types
from ...src.language import translate
from ...src.state.documents import Json
from ...src.serialization import mapping_value


def input_summary(example: Example, schema: Json) -> str:
    """Describe the inputs and controls needed by one workflow."""
    model = str(mapping_value(schema)["model"])
    has_image = "image" in example.sources
    live_kind = next(
        (kind for source, kind in (("source", "liveVideo"), ("image", "liveImage")) if source in example.sources),
        "liveText",
    )
    # Earlier conditions take priority when an example combines several input types.
    choices = (
        (example.mode == "webcam", "webcam"),
        (example.clip_count > 1, "continueImage" if has_image else "continueText"),
        (example.mode == "live", live_kind),
        (model == "ltx2", "speech"),
        (example.plan == "shots", "shots"),
        (example.plan == "prompts", "sequenceImage" if has_image else "sequenceText"),
        ("source" in example.sources, "reference" if "reference_image" in example.sources else "video"),
        (has_image and "ending_image" in example.sources, "firstLast"),
        ("ending_image" in example.sources, "last"),
        (has_image, "world" if example.mode != "record" else "image"),
    )
    fallback = "sound" if "AUDIO" in output_types(schema) else "text"
    key = next((key for applies, key in choices if applies), fallback)
    return translate("workflows", "index.input." + key)


def workflow_rows(schemas: dict[str, Json], guide_prefix: str) -> list[str]:
    """List each model's graphs under its own heading with their inputs and node guides."""
    groups: dict[str, list[Example]] = {}
    for example in sorted(EXAMPLES, key=lambda item: item.slug):
        groups.setdefault(str(mapping_value(schemas[example.node_id])["model"]), []).append(example)
    lines: list[str] = []
    guide = translate("workflows", "index.guide")
    for model, examples in groups.items():
        lines.extend([f"### {MODELS[model].title}", "", translate("workflows", "index.columns"), "| --- | --- | --- |"])
        lines.extend(
            f"| [{example.title}]({example.path}) | "
            f"{input_summary(example, schemas[example.node_id])} | [{guide}]({guide_prefix}/{example.node_id}.md) |"
            for example in examples
        )
        lines.append("")
    return lines


def sample_rows(sample_prefix: str) -> list[str]:
    """Link the shared sample inputs without copying media into each language build."""
    rows: list[str] = []
    for key, name in (
        ("forest", "forest-path.png"),
        ("illustration", "forest-illustration.png"),
        ("portrait", "fictional-portrait.png"),
        ("video", "forest-motion.mp4"),
    ):
        label = translate("workflows", "index." + key)
        purpose = translate("workflows", "index." + key + "Use")
        rows.append(f"| [{label}]({sample_prefix}/assets/{name}) | {purpose} |")
    return rows


def workflow_index(
    schemas: dict[str, Json],
    *,
    guide_prefix: str = "../web/docs",
    sample_prefix: str = ".",
    license_path: str = "../LICENSE.md",
) -> str:
    """Render translated instructions around stable workflow and resource paths."""
    lines: list[str] = []
    for key, heading in (
        ("title", "# "),
        ("intro", ""),
        ("openTitle", "## "),
        ("openSteps", ""),
        ("filesTitle", "## "),
    ):
        lines.extend(
            [
                heading
                + translate(
                    "workflows", "index." + key, count=len(EXAMPLES), start=translate("workflows", "notes.start")
                ),
                "",
            ]
        )
    lines.extend(workflow_rows(schemas, guide_prefix))
    for key, heading in (
        ("saveTitle", "## "),
        ("save", ""),
        ("stop", ""),
        ("help", ""),
        ("limitsTitle", "## "),
        ("limits", ""),
        ("updateTitle", "## "),
        ("update", ""),
        ("language", ""),
        ("samplesTitle", "## "),
        ("samples", ""),
    ):
        lines.extend(
            [heading + translate("workflows", "index." + key, save_video=translate("workflows", "nodes.saveVideo")), ""]
        )
    lines.extend([translate("workflows", "index.sampleColumns"), "| --- | --- |", *sample_rows(sample_prefix), ""])
    for key, heading in (
        ("reuseTitle", "### "),
        ("reuse", ""),
        ("videoDetails", ""),
        ("previewsTitle", "### "),
        ("previews", ""),
    ):
        lines.extend([heading + translate("workflows", "index." + key, license=license_path), ""])
    lines.extend([translate("workflows", "index.previewColumns"), "| --- | --- |"])
    for slug, label in (("fast-h3-01-text-to-video", "stream"), ("helios-02-image-to-video", "animated")):
        example = next(item for item in EXAMPLES if item.slug == slug)
        preview = translate("workflows", "index." + label)
        lines.append(f"| [{preview}]({sample_prefix}/{example.path[:-5]}.jpg) | [{example.title}]({example.path}) |")
    return "\n".join(lines) + "\n"
