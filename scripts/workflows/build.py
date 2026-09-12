"""Build portable ComfyUI templates without opening a host or provider session."""

import os
import sys
import json
import argparse
from pathlib import Path
from .layout import arrange
from .notes import sections
from .definitions import EXAMPLES
from .index import workflow_index
from ...src.state.documents import Json
from .models.longlive import SHOT_PROMPTS
from .models.helios import SEQUENCE_PROMPTS
from ...src.serialization import mapping_value
from ...src.language import translate, language_scope
from ..nodes.metadata import read_schemas, validate_metadata
from .example import (
    Example,
    FIRST_STEP_ID,
    GENERATION_ID,
    SAVE_AUDIO_ID,
    SAVE_VIDEO_ID,
    SETUP_NOTE_ID,
    USAGE_NOTE_ID,
    EXTRA_INPUT_ID,
    SECOND_STEP_ID,
    SOURCE_INPUT_ID,
)
from .serialize import (
    build_node,
    build_input,
    build_output,
    output_types,
    widget_values,
    save_workflows,
    validate_sources,
    native_widget_values,
    validate_node_sockets,
)


def build_workflow(example: Example, schemas: dict[str, Json], native: dict[str, Json]) -> dict[str, Json]:
    """Assemble one example with its notes, connected inputs, outputs, and arranged layout."""
    model = str(mapping_value(schemas[example.node_id])["model"])
    notes: list[Json] = [
        build_node(number, "MarkdownNote", [text], title=title)
        for number, title, text in zip(
            (SETUP_NOTE_ID, USAGE_NOTE_ID),
            (translate("workflows", "notes.start"), translate("workflows", "notes.usage")),
            sections(example, model),
            strict=True,
        )
        if text
    ]
    validate_sources(schemas[example.node_id], example.sources)
    widgets = widget_values(schemas[example.node_id], example.inputs)
    generation = build_node(GENERATION_ID, example.node_id, widgets, title=example.title)
    generation["outputs"] = [build_output("video", "VIDEO", [1]), build_output("metadata", "STRING", [])]
    save = build_node(
        SAVE_VIDEO_ID,
        "SaveVideo",
        native_widget_values("SaveVideo", native["SaveVideo"], f"video/reactor/{example.slug}"),
        title=translate("workflows", "nodes.saveVideo"),
    )
    save["inputs"] = [build_input("video", "VIDEO", 1)]
    save["outputs"] = [build_output("video", "VIDEO", [])]
    nodes: list[Json] = [*notes, generation, save]
    links: list[Json] = [[1, GENERATION_ID, 0, SAVE_VIDEO_ID, 0, "VIDEO"]]
    if "image" in example.sources:
        append_starting_image(nodes, links, generation, native)
    if "ending_image" in example.sources:
        append_ending_image(example, nodes, links, generation, native)
    if "source" in example.sources:
        append_source_video(example, nodes, links, generation, native)
    if example.plan == "shots":
        append_storyboard(nodes, links, generation, schemas)
    if "AUDIO" in output_types(schemas[example.node_id]):
        append_sound_output(example, nodes, links, generation, native)
    if example.plan == "prompts":
        append_prompt_sequence(example, nodes, links, generation, schemas)
    validate_node_sockets(nodes, schemas | native)
    extra = arrange(nodes, example, model)
    return {
        "last_node_id": 9,
        "last_link_id": len(links),
        "nodes": nodes,
        "links": links,
        "groups": [],
        "config": {},
        "extra": extra,
        "version": 0.4,
    }


def append_starting_image(
    nodes: list[Json], links: list[Json], generation: dict[str, Json], native: dict[str, Json]
) -> None:
    """Add the example's starting image and its connections."""
    input_node = build_node(
        SOURCE_INPUT_ID,
        "LoadImage",
        native_widget_values("LoadImage", native["LoadImage"]),
        title=translate("workflows", "nodes.startingImage"),
    )
    input_node["outputs"] = [build_output("IMAGE", "IMAGE", [2]), build_output("MASK", "MASK", [])]
    generation["inputs"] = [build_input("image", "IMAGE", 2)]
    links.append([2, SOURCE_INPUT_ID, 0, GENERATION_ID, 0, "IMAGE"])
    nodes.insert(1, input_node)


def append_ending_image(
    example: Example, nodes: list[Json], links: list[Json], generation: dict[str, Json], native: dict[str, Json]
) -> None:
    """Add the example's ending image and its connections."""
    link_id = len(links) + 1
    ending_image = build_node(
        EXTRA_INPUT_ID,
        "LoadImage",
        native_widget_values("LoadImage", native["LoadImage"]),
        title=translate("workflows", "nodes.endingImage"),
    )
    ending_image["outputs"] = [build_output("IMAGE", "IMAGE", [link_id]), build_output("MASK", "MASK", [])]
    incoming: list[Json] = [build_input("image", "IMAGE", 2)] if ("image" in example.sources) else []
    incoming.append(build_input("ending_image", "IMAGE", link_id))
    generation["inputs"] = incoming
    links.append([link_id, EXTRA_INPUT_ID, 0, GENERATION_ID, len(incoming) - 1, "IMAGE"])
    nodes.append(ending_image)


def append_source_video(
    example: Example, nodes: list[Json], links: list[Json], generation: dict[str, Json], native: dict[str, Json]
) -> None:
    """Add the example's source video and its connections."""
    input_node = build_node(
        SOURCE_INPUT_ID,
        "LoadVideo",
        native_widget_values("LoadVideo", native["LoadVideo"]),
        title=translate("workflows", "nodes.sourceVideo"),
    )
    input_node["outputs"] = [build_output("VIDEO", "VIDEO", [2])]
    generation["inputs"] = [build_input("source", "VIDEO", 2)]
    links.append([2, SOURCE_INPUT_ID, 0, GENERATION_ID, 0, "VIDEO"])
    nodes.insert(1, input_node)
    if "reference_image" in example.sources:
        reference = build_node(
            EXTRA_INPUT_ID,
            "LoadImage",
            native_widget_values("LoadImage", native["LoadImage"]),
            title=translate("workflows", "nodes.referenceImage"),
        )
        reference["outputs"] = [build_output("IMAGE", "IMAGE", [3]), build_output("MASK", "MASK", [])]
        generation["inputs"] = [build_input("source", "VIDEO", 2), build_input("reference_image", "IMAGE", 3)]
        links.append([3, EXTRA_INPUT_ID, 0, GENERATION_ID, 1, "IMAGE"])
        nodes.append(reference)


def append_storyboard(
    nodes: list[Json], links: list[Json], generation: dict[str, Json], schemas: dict[str, Json]
) -> None:
    """Add the example's storyboard and its connections."""
    first = build_node(
        FIRST_STEP_ID,
        "ReactorIncLongLiveAddShot",
        widget_values(
            schemas["ReactorIncLongLiveAddShot"],
            {
                "previous": "[]",
                "at_session_chunk": 1,
                "transition": "soft",
                "prompt": SHOT_PROMPTS["soft_transition"],
            },
        ),
        title=translate("workflows", "nodes.softTransition"),
    )
    first["outputs"] = [build_output("storyboard", "STRING", [2])]
    second = build_node(
        SECOND_STEP_ID,
        "ReactorIncLongLiveAddShot",
        widget_values(
            schemas["ReactorIncLongLiveAddShot"],
            {
                "previous": "[]",
                "at_session_chunk": 2,
                "transition": "cut",
                "prompt": SHOT_PROMPTS["hard_cut"],
            },
        ),
        title=translate("workflows", "nodes.hardCut"),
    )
    second["inputs"] = [build_input("previous", "STRING", 2, has_widget=True)]
    second["outputs"] = [build_output("storyboard", "STRING", [3])]
    generation["inputs"] = [build_input("storyboard", "STRING", 3, has_widget=True)]
    links.extend(
        [[2, FIRST_STEP_ID, 0, SECOND_STEP_ID, 0, "STRING"], [3, SECOND_STEP_ID, 0, GENERATION_ID, 0, "STRING"]]
    )
    nodes.extend([first, second])


def append_sound_output(
    example: Example, nodes: list[Json], links: list[Json], generation: dict[str, Json], native: dict[str, Json]
) -> None:
    """Add the example's sound output and its connections."""
    link_id = len(links) + 1
    generation["outputs"] = [
        build_output("video", "VIDEO", [1]),
        build_output("audio", "AUDIO", [link_id]),
        build_output("metadata", "STRING", []),
    ]
    sound = build_node(
        SAVE_AUDIO_ID,
        "SaveAudioAdvanced",
        native_widget_values("SaveAudioAdvanced", native["SaveAudioAdvanced"], f"audio/reactor/{example.slug}"),
        title=translate("workflows", "nodes.saveAudio"),
    )
    sound["inputs"] = [build_input("audio", "AUDIO", link_id)]
    sound["outputs"] = [build_output("audio", "AUDIO", [])]
    links.append([link_id, GENERATION_ID, 1, SAVE_AUDIO_ID, 0, "AUDIO"])
    nodes.append(sound)


def append_prompt_sequence(
    example: Example, nodes: list[Json], links: list[Json], generation: dict[str, Json], schemas: dict[str, Json]
) -> None:
    """Add the example's prompt sequence and its connections."""
    first_link = len(links) + 1
    second_link = first_link + 1
    first = build_node(
        FIRST_STEP_ID,
        "ReactorIncHeliosAddPrompt",
        widget_values(
            schemas["ReactorIncHeliosAddPrompt"],
            {"previous": "[]", "chunk": 1, "prompt": SEQUENCE_PROMPTS["sunlight"]},
        ),
        title=translate("workflows", "nodes.sunlight"),
    )
    first["outputs"] = [build_output("sequence", "STRING", [first_link])]
    second = build_node(
        SECOND_STEP_ID,
        "ReactorIncHeliosAddPrompt",
        widget_values(
            schemas["ReactorIncHeliosAddPrompt"],
            {"previous": "[]", "chunk": 3, "prompt": SEQUENCE_PROMPTS["clearing"]},
        ),
        title=translate("workflows", "nodes.clearing"),
    )
    second["inputs"] = [build_input("previous", "STRING", first_link, has_widget=True)]
    second["outputs"] = [build_output("sequence", "STRING", [second_link])]
    incoming: list[Json] = [build_input("image", "IMAGE", 2)] if ("image" in example.sources) else []
    incoming.append(build_input("sequence", "STRING", second_link, has_widget=True))
    generation["inputs"] = incoming
    links.extend(
        [
            [first_link, FIRST_STEP_ID, 0, SECOND_STEP_ID, 0, "STRING"],
            [second_link, SECOND_STEP_ID, 0, GENERATION_ID, len(incoming) - 1, "STRING"],
        ]
    )
    nodes.extend([first, second])


def arguments() -> argparse.Namespace:
    """Read build options without changing files or importing the host."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--language", default="en", help="Language for workflow labels and notes; missing messages use English."
    )
    parser.add_argument("--output-directory", type=Path, help="Output folder; required for non-English workflows.")
    return parser.parse_args()


def main() -> int:
    """Build or check every registered example and its index; report uncovered nodes and extra files."""
    args = arguments()
    root = Path(__file__).resolve().parents[2]
    canonical = root / "workflows"
    destination = args.output_directory.resolve() if args.output_directory else canonical
    if args.language.lower() != "en" and (destination == canonical or destination.is_relative_to(canonical)):
        sys.stderr.write("Choose --output-directory outside workflows/ for a non-English build.\n")
        return 2
    schema_export = read_schemas()
    schemas = mapping_value(schema_export["reactor"])
    native = mapping_value(schema_export["native"])
    issues = validate_metadata(schemas)
    covered = {example.node_id for example in EXAMPLES}
    if any((example.plan == "shots") for example in EXAMPLES):
        covered.add("ReactorIncLongLiveAddShot")
    if any((example.plan == "prompts") for example in EXAMPLES):
        covered.add("ReactorIncHeliosAddPrompt")
    issues.extend(f"Add a workflow for {name}." for name in sorted(set(schemas) - covered))
    expected = {example.path for example in EXAMPLES}
    with language_scope(args.language):
        generated = {
            destination / example.path: json.dumps(
                build_workflow(example, schemas, native), indent=2, ensure_ascii=False
            )
            + "\n"
            for example in EXAMPLES
        }
        generated[destination / "README.md"] = workflow_index(
            schemas,
            guide_prefix=Path(os.path.relpath(root / "web/docs", destination)).as_posix(),
            sample_prefix=Path(os.path.relpath(canonical, destination)).as_posix(),
            license_path=Path(os.path.relpath(root / "LICENSE.md", destination)).as_posix(),
        )
    issues.extend(
        f"Review the unindexed workflow {path.name}."
        for path in destination.rglob("*.json")
        if path.relative_to(destination).as_posix() not in expected
    )
    if not issues:
        issues.extend(save_workflows(generated, check=args.check))
    for issue in issues:
        sys.stdout.write(issue + "\n")
    return int(bool(issues))


if __name__ == "__main__":
    raise SystemExit(main())
