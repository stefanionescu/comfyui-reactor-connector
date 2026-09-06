"""Build portable ComfyUI templates without opening a host or provider session."""

import argparse
import json
from pathlib import Path

from reactor_comfy.json_data import Json
from reactor_comfy.node_catalog import NODE_MODELS

from .live_examples import LIVE_NODE_IDS
from .workflow_definitions import EXAMPLES, Example
from .workflow_index import workflow_index
from .workflow_layout import arrange
from .workflow_notes import sections


def node(
    number: int, kind: str, widgets: list[Json], *, title: str | None = None
) -> dict[str, Json]:
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
    return {"name": name, "type": kind, "links": links}


def linked(name: str, kind: str, link: int, *, widget: bool = False) -> dict[str, Json]:
    value: dict[str, Json] = {"name": name, "type": kind, "link": link}
    if widget:
        value["widget"] = {"name": name}
    return value


def build_workflow(example: Example) -> dict[str, Json]:
    notes: list[Json] = [
        node(number, "MarkdownNote", [text], title=title)
        for number, title, text in zip(
            (1, 8),
            ("Start here", "Using this workflow"),
            sections(example),
            strict=True,
        )
        if text
    ]
    widgets: list[Json] = [example.prompt, example.duration_seconds / example.clip_count]
    if example.seed:
        widgets.extend([42, "fixed"])
    widgets.extend([0, *example.controls])
    if example.storyboard or example.prompt_sequence:
        widgets.append("[]")
    if example.node_id in LIVE_NODE_IDS:
        widgets.append(example.panel)
    render = node(3, example.node_id, widgets, title=example.title)
    render["outputs"] = [output("video", "VIDEO", [1]), output("metadata", "STRING", [])]
    save = node(
        4,
        "SaveVideo",
        [f"video/reactor/{example.slug}", "auto", "auto"],
        title="Preview and save video",
    )
    save["inputs"] = [linked("video", "VIDEO", 1)]
    nodes: list[Json] = [*notes, render, save]
    links: list[Json] = [[1, 3, 0, 4, 0, "VIDEO"]]
    if example.image:
        load = node(2, "LoadImage", ["", "image"], title="Upload your starting image")
        load["outputs"] = [output("IMAGE", "IMAGE", [2]), output("MASK", "MASK", [])]
        render["inputs"] = [linked("image", "IMAGE", 2)]
        links.append([2, 2, 0, 3, 0, "IMAGE"])
        nodes.insert(1, load)
    if example.ending_image:
        link_id = len(links) + 1
        final_image = node(5, "LoadImage", ["", "image"], title="Choose the final frame")
        final_image["outputs"] = [output("IMAGE", "IMAGE", [link_id]), output("MASK", "MASK", [])]
        incoming: list[Json] = [linked("image", "IMAGE", 2)] if example.image else []
        incoming.append(linked("ending_image", "IMAGE", link_id))
        render["inputs"] = incoming
        links.append([link_id, 5, 0, 3, len(incoming) - 1, "IMAGE"])
        nodes.append(final_image)
    if example.video:
        load = node(2, "LoadVideo", [""], title="Upload your source video")
        load["outputs"] = [output("VIDEO", "VIDEO", [2])]
        render["inputs"] = [linked("source", "VIDEO", 2)]
        links.append([2, 2, 0, 3, 0, "VIDEO"])
        nodes.insert(1, load)
        if example.reference:
            reference = node(5, "LoadImage", ["", "image"], title="Upload your reference subject")
            reference["outputs"] = [output("IMAGE", "IMAGE", [3]), output("MASK", "MASK", [])]
            render["inputs"] = [linked("source", "VIDEO", 2), linked("reference_image", "IMAGE", 3)]
            links.append([3, 5, 0, 3, 1, "IMAGE"])
            nodes.append(reference)
    if example.storyboard:
        first = node(
            5,
            "ReactorIncLongLiveAddShot",
            ["[]", 1, "soft", "The camera pulls back to show the trees around the fox."],
            title="1. Soft transition",
        )
        first["outputs"] = [output("storyboard", "STRING", [2])]
        second = node(
            6,
            "ReactorIncLongLiveAddShot",
            ["[]", 2, "cut", "A wide view of a still lake at sunrise."],
            title="2. Hard cut",
        )
        second["inputs"] = [linked("previous", "STRING", 2, widget=True)]
        second["outputs"] = [output("storyboard", "STRING", [3])]
        render["inputs"] = [linked("storyboard", "STRING", 3, widget=True)]
        links.extend([[2, 5, 0, 6, 0, "STRING"], [3, 6, 0, 3, 0, "STRING"]])
        nodes.extend([first, second])
    if example.audio:
        link_id = len(links) + 1
        render["outputs"] = [
            output("video", "VIDEO", [1]),
            output("audio", "AUDIO", [link_id]),
            output("metadata", "STRING", []),
        ]
        sound = node(
            7,
            "SaveAudioAdvanced",
            [f"audio/reactor/{example.slug}", "flac"],
            title="Preview and save sound",
        )
        sound["inputs"] = [linked("audio", "AUDIO", link_id)]
        sound["outputs"] = [output("audio", "AUDIO", [])]
        links.append([link_id, 3, 1, 7, 0, "AUDIO"])
        nodes.append(sound)
    if example.prompt_sequence:
        first_link = len(links) + 1
        second_link = first_link + 1
        first = node(
            5,
            "ReactorIncHeliosAddPrompt",
            ["[]", 1, "Sunlight reaches the forest floor as the camera moves forward."],
            title="1. Let sunlight through",
        )
        first["outputs"] = [output("sequence", "STRING", [first_link])]
        second = node(
            6,
            "ReactorIncHeliosAddPrompt",
            ["[]", 3, "The camera follows the path into a sunny clearing."],
            title="2. Enter a clearing",
        )
        second["inputs"] = [linked("previous", "STRING", first_link, widget=True)]
        second["outputs"] = [output("sequence", "STRING", [second_link])]
        incoming = [linked("image", "IMAGE", 2)] if example.image else []
        incoming.append(linked("sequence", "STRING", second_link, widget=True))
        render["inputs"] = incoming
        links.extend(
            [
                [first_link, 5, 0, 6, 0, "STRING"],
                [second_link, 6, 0, 3, len(incoming) - 1, "STRING"],
            ]
        )
        nodes.extend([first, second])
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    destination = root / "workflows"
    issues: list[str] = []
    covered = {example.node_id for example in EXAMPLES}
    if any(example.storyboard for example in EXAMPLES):
        covered.add("ReactorIncLongLiveAddShot")
    if any(example.prompt_sequence for example in EXAMPLES):
        covered.add("ReactorIncHeliosAddPrompt")
    issues.extend(f"Add a workflow for {name}." for name in sorted(set(NODE_MODELS) - covered))
    for example in EXAMPLES:
        text = json.dumps(build_workflow(example), indent=2, ensure_ascii=False) + "\n"
        path = destination / example.path
        if args.check:
            if not path.exists() or path.read_text() != text:
                issues.append(f"Rebuild workflow {example.slug}.")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    expected = {example.path for example in EXAMPLES}
    index_path = destination / "README.md"
    if args.check:
        if not index_path.exists() or index_path.read_text() != workflow_index():
            issues.append("Rebuild the workflow index with mise run workflows:build.")
    else:
        index_path.write_text(workflow_index())
    issues.extend(
        f"Review the unindexed workflow {path.name}."
        for path in destination.rglob("*.json")
        if path.relative_to(destination).as_posix() not in expected
    )
    for issue in issues:
        print(issue)
    return int(bool(issues))


if __name__ == "__main__":
    raise SystemExit(main())
