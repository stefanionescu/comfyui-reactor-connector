"""Build portable ComfyUI templates without opening a host or provider session."""

import sys
import json
from pathlib import Path
import argparse

from .index import EXAMPLE_DIRECTORY, readme_issues
from .notes import sections
from .texts import NODES, NOTES, TITLES
from .layout import arrange
from .example import (
    GENERATION_ID,
    SAVE_VIDEO_ID,
    SETUP_NOTE_ID,
    USAGE_NOTE_ID,
    Example,
)
from .serialize import (
    build_node,
    build_input,
    output_types,
    widget_values,
    save_workflows,
    validate_sources,
    native_widget_values,
    validate_node_sockets,
)
from .connections import (
    append_storyboard,
    append_ending_image,
    append_sound_output,
    append_source_video,
    append_starting_image,
    append_prompt_sequence,
)
from .definitions import EXAMPLES
from ..nodes.metadata import read_schemas, validate_metadata
from ...src.serialization import Json, mapping_value


def build_workflow(example: Example, schemas: dict[str, Json], native: dict[str, Json]) -> dict[str, Json]:
    """Assemble one example with its notes, connected inputs, outputs, and arranged layout.

    Args:
        example: The example to build.
        schemas: The schemas of the Reactor nodes, by node ID.
        native: The schemas of the host nodes, by node ID.

    Returns:
        The workflow document that ComfyUI loads.

    """
    model = example.model
    notes: list[Json] = [
        build_node(number, 'MarkdownNote', [text], title=title)
        for number, title, text in zip(
            (SETUP_NOTE_ID, USAGE_NOTE_ID),
            (NOTES['start'], NOTES['usage']),
            sections(example, model),
            strict=True,
        )
        if text
    ]
    validate_sources(schemas[example.node_id], example.sources)
    widgets = widget_values(schemas[example.node_id], example.inputs)
    generation = build_node(GENERATION_ID, example.node_id, widgets, title=TITLES[example.slug])
    generation['outputs'] = [{'name': 'video', 'type': 'VIDEO', 'links': [1]}]
    save = build_node(
        SAVE_VIDEO_ID,
        'SaveVideo',
        native_widget_values('SaveVideo', native['SaveVideo'], f'video/reactor/{example.slug}'),
        title=NODES['saveVideo'],
    )
    save['inputs'] = [build_input('video', 'VIDEO', 1)]
    save['outputs'] = [{'name': 'video', 'type': 'VIDEO', 'links': []}]
    nodes: list[Json] = [*notes, generation, save]
    links: list[Json] = [[1, GENERATION_ID, 0, SAVE_VIDEO_ID, 0, 'VIDEO']]
    if 'image' in example.sources:
        append_starting_image(nodes, links, generation, native)
    if 'ending_image' in example.sources:
        append_ending_image(example, nodes, links, generation, native)
    if 'source' in example.sources:
        append_source_video(example, nodes, links, generation, native)
    if example.plan == 'shots':
        append_storyboard(nodes, links, generation, schemas)
    if 'AUDIO' in output_types(schemas[example.node_id]):
        append_sound_output(example, nodes, links, generation, native)
    if example.plan == 'prompts':
        append_prompt_sequence(example, nodes, links, generation, schemas)
    validate_node_sockets(nodes, schemas | native)
    extra = arrange(nodes, example, model)
    return {
        'last_node_id': 9,
        'last_link_id': len(links),
        'nodes': nodes,
        'links': links,
        'groups': [],
        'config': {},
        'extra': extra,
        'version': 0.4,
    }


def arguments() -> argparse.Namespace:
    """Read build options without changing files or importing the host.

    Returns:
        The parsed options.

    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--output-directory', type=Path, help='Output folder; defaults to the shipped examples.')
    return parser.parse_args()


def main() -> int:
    """Build or check every registered example and its index; report uncovered nodes and extra files.

    Returns:
        The exit status, which is 1 when a check reports an issue.

    """
    args = arguments()
    root = Path(__file__).resolve().parents[2]
    canonical = root / EXAMPLE_DIRECTORY
    destination = args.output_directory.resolve() if args.output_directory else canonical
    schema_export = read_schemas()
    schemas = mapping_value(schema_export['reactor'])
    native = mapping_value(schema_export['native'])
    issues = validate_metadata(schemas)
    covered = {example.node_id for example in EXAMPLES}
    if any((example.plan == 'shots') for example in EXAMPLES):
        covered.add('ReactorIncLongLiveAddShot')
    if any((example.plan == 'prompts') for example in EXAMPLES):
        covered.add('ReactorIncHeliosAddPrompt')
    issues.extend(f'Add a workflow for {name}.' for name in sorted(set(schemas) - covered))
    issues.extend(readme_issues(root))
    expected = {f'{example.slug}.json' for example in EXAMPLES}
    generated = {
        destination / f'{example.slug}.json': json.dumps(
            build_workflow(example, schemas, native), indent=2, ensure_ascii=False
        )
        + '\n'
        for example in EXAMPLES
    }
    issues.extend(
        f'Review the unindexed workflow {path.name}.'
        for path in destination.rglob('*.json')
        if path.relative_to(destination).as_posix() not in expected
    )
    if not issues:
        issues.extend(save_workflows(generated, check=args.check))
    for issue in issues:
        sys.stdout.write(issue + '\n')
    return int(bool(issues))


if __name__ == '__main__':
    raise SystemExit(main())
