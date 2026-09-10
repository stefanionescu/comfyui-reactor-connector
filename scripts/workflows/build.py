"""Build portable ComfyUI templates without opening a host or provider session."""

import os
import sys
import json
import argparse
from pathlib import Path
from .layout import arrange
from .notes import sections
from .example import Example
from .definitions import EXAMPLES
from .index import workflow_index
from ...src.serialization import Json
from ..docs.build import inventory_issues
from .models.longlive import SHOT_PROMPTS
from .models.helios import SEQUENCE_PROMPTS
from ...src.language import translate, language_scope
from ..nodes.metadata import read_schemas, validate_metadata
from .serialize import widget_values, validate_sources, validate_connections, output_types


def node(number: int, kind: str, widgets: list[Json], *, title: str | None = None) -> dict[str, Json]:
    """Create a serialized ComfyUI node with stable widget order and an optional display title."""
    value: dict[str, Json] = {
        "id": number,
        "type": kind,
        "pos": [0, 0],
        "size": [0, 0],
        "flags": {},
        "order": number,
        "mode": 0,
        "inputs": [],
        "outputs": [],
        "properties": {"Node name for S&R": kind},
        "widgets_values": widgets,
    }
    if title:
        value["title"] = title
    return value


def output(name: str, kind: str, links: list[Json]) -> dict[str, Json]:
    """Describe a serialized output socket and its links."""
    return {"name": name, "type": kind, "links": links}


def linked(name: str, kind: str, link: int, *, widget: bool = False) -> dict[str, Json]:
    """Describe a connected input and its optional widget binding."""
    value: dict[str, Json] = {"name": name, "type": kind, "link": link}
    if widget:
        value["widget"] = {"name": name}
    return value


def build_workflow(example: Example, schemas: dict[str, Json]) -> dict[str, Json]:
    """Assemble one example with its notes, connected inputs, outputs, and arranged layout."""
    notes: list[Json] = [
        node(number, "MarkdownNote", [text], title=title)
        for number, title, text in zip(
            (1, 8),
            (translate("workflows", "notes.start"), translate("workflows", "notes.usage")),
            sections(example),
            strict=True,
        )
        if text
    ]
    validate_sources(schemas[example.node_id], example.sources)
    widgets = widget_values(schemas[example.node_id], example.inputs)
    generation = node(3, example.node_id, widgets, title=example.title)
    generation["outputs"] = [output("video", "VIDEO", [1]), output("metadata", "STRING", [])]
    save = node(
        4,
        "SaveVideo",
        [f"video/reactor/{example.slug}", "auto", "auto"],
        title=translate("workflows", "nodes.saveVideo"),
    )
    save["inputs"] = [linked("video", "VIDEO", 1)]
    nodes: list[Json] = [*notes, generation, save]
    links: list[Json] = [[1, 3, 0, 4, 0, "VIDEO"]]
    if "image" in example.sources:
        append_starting_image(nodes, links, generation)
    if "ending_image" in example.sources:
        append_ending_image(example, nodes, links, generation)
    if "source" in example.sources:
        append_source_video(example, nodes, links, generation)
    if example.plan == "shots":
        append_storyboard(nodes, links, generation, schemas)
    if "AUDIO" in output_types(schemas[example.node_id]):
        append_sound_output(example, nodes, links, generation)
    if example.plan == "prompts":
        append_prompt_sequence(example, nodes, links, generation, schemas)
    validate_connections(nodes, schemas)
    extra = arrange(nodes, example)
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


def append_starting_image(nodes: list[Json], links: list[Json], generation: dict[str, Json]) -> None:
    """Add the example's starting image and its connections."""
    input_node = node(
        2,
        "LoadImage",
        ["", "image"],
        title=translate("workflows", "nodes.startingImage"),
    )
    input_node["outputs"] = [output("IMAGE", "IMAGE", [2]), output("MASK", "MASK", [])]
    generation["inputs"] = [linked("image", "IMAGE", 2)]
    links.append([2, 2, 0, 3, 0, "IMAGE"])
    nodes.insert(1, input_node)


def append_ending_image(example: Example, nodes: list[Json], links: list[Json], generation: dict[str, Json]) -> None:
    """Add the example's ending image and its connections."""
    link_id = len(links) + 1
    ending_image = node(
        5,
        "LoadImage",
        ["", "image"],
        title=translate("workflows", "nodes.endingImage"),
    )
    ending_image["outputs"] = [output("IMAGE", "IMAGE", [link_id]), output("MASK", "MASK", [])]
    incoming: list[Json] = [linked("image", "IMAGE", 2)] if ("image" in example.sources) else []
    incoming.append(linked("ending_image", "IMAGE", link_id))
    generation["inputs"] = incoming
    links.append([link_id, 5, 0, 3, len(incoming) - 1, "IMAGE"])
    nodes.append(ending_image)


def append_source_video(example: Example, nodes: list[Json], links: list[Json], generation: dict[str, Json]) -> None:
    """Add the example's source video and its connections."""
    input_node = node(
        2,
        "LoadVideo",
        [""],
        title=translate("workflows", "nodes.sourceVideo"),
    )
    input_node["outputs"] = [output("VIDEO", "VIDEO", [2])]
    generation["inputs"] = [linked("source", "VIDEO", 2)]
    links.append([2, 2, 0, 3, 0, "VIDEO"])
    nodes.insert(1, input_node)
    if "reference_image" in example.sources:
        reference = node(
            5,
            "LoadImage",
            ["", "image"],
            title=translate("workflows", "nodes.referenceImage"),
        )
        reference["outputs"] = [output("IMAGE", "IMAGE", [3]), output("MASK", "MASK", [])]
        generation["inputs"] = [linked("source", "VIDEO", 2), linked("reference_image", "IMAGE", 3)]
        links.append([3, 5, 0, 3, 1, "IMAGE"])
        nodes.append(reference)


def append_storyboard(
    nodes: list[Json], links: list[Json], generation: dict[str, Json], schemas: dict[str, Json]
) -> None:
    """Add the example's storyboard and its connections."""
    first = node(
        5,
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
    first["outputs"] = [output("storyboard", "STRING", [2])]
    second = node(
        6,
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
    second["inputs"] = [linked("previous", "STRING", 2, widget=True)]
    second["outputs"] = [output("storyboard", "STRING", [3])]
    generation["inputs"] = [linked("storyboard", "STRING", 3, widget=True)]
    links.extend([[2, 5, 0, 6, 0, "STRING"], [3, 6, 0, 3, 0, "STRING"]])
    nodes.extend([first, second])


def append_sound_output(example: Example, nodes: list[Json], links: list[Json], generation: dict[str, Json]) -> None:
    """Add the example's sound output and its connections."""
    link_id = len(links) + 1
    generation["outputs"] = [
        output("video", "VIDEO", [1]),
        output("audio", "AUDIO", [link_id]),
        output("metadata", "STRING", []),
    ]
    sound = node(
        7,
        "SaveAudioAdvanced",
        [f"audio/reactor/{example.slug}", "flac"],
        title=translate("workflows", "nodes.saveAudio"),
    )
    sound["inputs"] = [linked("audio", "AUDIO", link_id)]
    sound["outputs"] = [output("audio", "AUDIO", [])]
    links.append([link_id, 3, 1, 7, 0, "AUDIO"])
    nodes.append(sound)


def append_prompt_sequence(
    example: Example, nodes: list[Json], links: list[Json], generation: dict[str, Json], schemas: dict[str, Json]
) -> None:
    """Add the example's prompt sequence and its connections."""
    first_link = len(links) + 1
    second_link = first_link + 1
    first = node(
        5,
        "ReactorIncHeliosAddPrompt",
        widget_values(
            schemas["ReactorIncHeliosAddPrompt"],
            {"previous": "[]", "chunk": 1, "prompt": SEQUENCE_PROMPTS["sunlight"]},
        ),
        title=translate("workflows", "nodes.sunlight"),
    )
    first["outputs"] = [output("sequence", "STRING", [first_link])]
    second = node(
        6,
        "ReactorIncHeliosAddPrompt",
        widget_values(
            schemas["ReactorIncHeliosAddPrompt"],
            {"previous": "[]", "chunk": 3, "prompt": SEQUENCE_PROMPTS["clearing"]},
        ),
        title=translate("workflows", "nodes.clearing"),
    )
    second["inputs"] = [linked("previous", "STRING", first_link, widget=True)]
    second["outputs"] = [output("sequence", "STRING", [second_link])]
    incoming: list[Json] = [linked("image", "IMAGE", 2)] if ("image" in example.sources) else []
    incoming.append(linked("sequence", "STRING", second_link, widget=True))
    generation["inputs"] = incoming
    links.extend(
        [
            [first_link, 5, 0, 6, 0, "STRING"],
            [second_link, 6, 0, 3, len(incoming) - 1, "STRING"],
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
    schemas = read_schemas()
    issues = validate_metadata(schemas)
    issues.extend(inventory_issues(root / "web/docs", root / "web/dist/docs", set(schemas)))
    covered = {example.node_id for example in EXAMPLES}
    if any((example.plan == "shots") for example in EXAMPLES):
        covered.add("ReactorIncLongLiveAddShot")
    if any((example.plan == "prompts") for example in EXAMPLES):
        covered.add("ReactorIncHeliosAddPrompt")
    issues.extend(f"Add a workflow for {name}." for name in sorted(set(schemas) - covered))
    expected = {example.path for example in EXAMPLES}
    with language_scope(args.language):
        generated = {
            destination / example.path: json.dumps(build_workflow(example, schemas), indent=2, ensure_ascii=False)
            + "\n"
            for example in EXAMPLES
        }
        generated[destination / "README.md"] = workflow_index(
            schemas,
            guide_prefix=Path(os.path.relpath(root / "web/docs", destination)).as_posix(),
            sample_prefix=Path(os.path.relpath(canonical, destination)).as_posix(),
            license_path=Path(os.path.relpath(root / "LICENSE.md", destination)).as_posix(),
        )
    for path, text in generated.items():
        if args.check:
            if not path.exists() or path.read_text() != text:
                issues.append(f"Rebuild {path.name} with mise run workflows:build.")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    issues.extend(
        f"Review the unindexed workflow {path.name}."
        for path in destination.rglob("*.json")
        if path.relative_to(destination).as_posix() not in expected
    )
    for issue in issues:
        sys.stdout.write(issue + "\n")
    return int(bool(issues))


if __name__ == "__main__":
    raise SystemExit(main())
