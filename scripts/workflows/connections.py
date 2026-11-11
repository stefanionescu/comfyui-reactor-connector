"""Append the input, output, and sequence nodes that an example connects to its generation node."""

from .texts import NODES
from .example import (
    FIRST_STEP_ID,
    GENERATION_ID,
    SAVE_AUDIO_ID,
    EXTRA_INPUT_ID,
    SECOND_STEP_ID,
    SOURCE_INPUT_ID,
    Example,
)
from .serialize import (
    build_node,
    build_input,
    widget_values,
    native_widget_values,
)
from .models.helios import SEQUENCE_PROMPTS
from .models.longlive import SHOT_PROMPTS
from ...src.serialization import Json


def append_starting_image(
    nodes: list[Json], links: list[Json], generation: dict[str, Json], native: dict[str, Json]
) -> None:
    """Add the example's starting image and its connections.

    Args:
        nodes: The workflow nodes, which receive the image loader.
        links: The workflow links, which receive the image link.
        generation: The generation node, which receives the image input.
        native: The schemas of the host nodes, which hold the image loader.

    """
    input_node = build_node(
        SOURCE_INPUT_ID,
        'LoadImage',
        native_widget_values('LoadImage', native['LoadImage']),
        title=NODES['portraitImage' if generation['type'] == 'ReactorIncLtxSpeak' else 'startingImage'],
    )
    input_node['outputs'] = [
        {'name': 'IMAGE', 'type': 'IMAGE', 'links': [2]},
        {'name': 'MASK', 'type': 'MASK', 'links': []},
    ]
    generation['inputs'] = [build_input('image', 'IMAGE', 2)]
    links.append([2, SOURCE_INPUT_ID, 0, GENERATION_ID, 0, 'IMAGE'])
    nodes.insert(1, input_node)


def append_ending_image(
    example: Example, nodes: list[Json], links: list[Json], generation: dict[str, Json], native: dict[str, Json]
) -> None:
    """Add the example's ending image and its connections.

    Args:
        example: The example, whose sources decide the input position.
        nodes: The nodes of the workflow, to which the loader is added.
        links: The links of the workflow, to which the new link is added.
        generation: The generation node, which receives the ending image input.
        native: The host node schemas, which hold the image loader.

    """
    link_id = len(links) + 1
    ending_image = build_node(
        EXTRA_INPUT_ID,
        'LoadImage',
        native_widget_values('LoadImage', native['LoadImage']),
        title=NODES['endingImage'],
    )
    ending_image['outputs'] = [
        {'name': 'IMAGE', 'type': 'IMAGE', 'links': [link_id]},
        {'name': 'MASK', 'type': 'MASK', 'links': []},
    ]
    incoming: list[Json] = [build_input('image', 'IMAGE', 2)] if ('image' in example.sources) else []
    incoming.append(build_input('ending_image', 'IMAGE', link_id))
    generation['inputs'] = incoming
    links.append([link_id, EXTRA_INPUT_ID, 0, GENERATION_ID, len(incoming) - 1, 'IMAGE'])
    nodes.append(ending_image)


def append_source_video(
    example: Example, nodes: list[Json], links: list[Json], generation: dict[str, Json], native: dict[str, Json]
) -> None:
    """Add the example's source video and its connections.

    Args:
        example: The example, whose sources decide whether a reference image follows.
        nodes: The node list that receives the video loader.
        links: The link list that receives the video link.
        generation: The generation node, which receives the source input.
        native: The host node schemas, which hold both loaders.

    """
    input_node = build_node(
        SOURCE_INPUT_ID,
        'LoadVideo',
        native_widget_values('LoadVideo', native['LoadVideo']),
        title=NODES['sourceVideo'],
    )
    input_node['outputs'] = [{'name': 'VIDEO', 'type': 'VIDEO', 'links': [2]}]
    generation['inputs'] = [build_input('source', 'VIDEO', 2)]
    links.append([2, SOURCE_INPUT_ID, 0, GENERATION_ID, 0, 'VIDEO'])
    nodes.insert(1, input_node)
    if 'reference_image' in example.sources:
        reference = build_node(
            EXTRA_INPUT_ID,
            'LoadImage',
            native_widget_values('LoadImage', native['LoadImage']),
            title=NODES['referenceImage'],
        )
        reference['outputs'] = [
            {'name': 'IMAGE', 'type': 'IMAGE', 'links': [3]},
            {'name': 'MASK', 'type': 'MASK', 'links': []},
        ]
        generation['inputs'] = [build_input('source', 'VIDEO', 2), build_input('reference_image', 'IMAGE', 3)]
        links.append([3, EXTRA_INPUT_ID, 0, GENERATION_ID, 1, 'IMAGE'])
        nodes.append(reference)


def append_storyboard(
    nodes: list[Json], links: list[Json], generation: dict[str, Json], schemas: dict[str, Json]
) -> None:
    """Add the example's storyboard and its connections.

    Args:
        nodes: The node list that receives both shot nodes.
        links: The link list that receives the storyboard links.
        generation: The generation node, which receives the storyboard input.
        schemas: The Reactor node schemas, which hold the shot node.

    """
    first = build_node(
        FIRST_STEP_ID,
        'ReactorIncLongLiveAddShot',
        widget_values(
            schemas['ReactorIncLongLiveAddShot'],
            {
                'previous': '[]',
                'at_session_chunk': 1,
                'transition': 'soft',
                'prompt': SHOT_PROMPTS['soft_transition'],
            },
        ),
        title=NODES['softTransition'],
    )
    first['outputs'] = [{'name': 'storyboard', 'type': 'STRING', 'links': [2]}]
    second = build_node(
        SECOND_STEP_ID,
        'ReactorIncLongLiveAddShot',
        widget_values(
            schemas['ReactorIncLongLiveAddShot'],
            {
                'previous': '[]',
                'at_session_chunk': 2,
                'transition': 'cut',
                'prompt': SHOT_PROMPTS['hard_cut'],
            },
        ),
        title=NODES['hardCut'],
    )
    second['inputs'] = [build_input('previous', 'STRING', 2, has_widget=True)]
    second['outputs'] = [{'name': 'storyboard', 'type': 'STRING', 'links': [3]}]
    generation['inputs'] = [build_input('storyboard', 'STRING', 3, has_widget=True)]
    links.extend(
        [[2, FIRST_STEP_ID, 0, SECOND_STEP_ID, 0, 'STRING'], [3, SECOND_STEP_ID, 0, GENERATION_ID, 0, 'STRING']]
    )
    nodes.extend([first, second])


def append_sound_output(
    example: Example, nodes: list[Json], links: list[Json], generation: dict[str, Json], native: dict[str, Json]
) -> None:
    """Add the example's sound output and its connections.

    Args:
        example: The example, whose slug names the saved sound.
        nodes: The node list that receives the node that saves sound.
        links: The link list that receives the audio link.
        generation: The generation node, which receives the audio output.
        native: The host node schemas, which hold the node that saves sound.

    """
    link_id = len(links) + 1
    generation['outputs'] = [
        {'name': 'video', 'type': 'VIDEO', 'links': [1]},
        {'name': 'audio', 'type': 'AUDIO', 'links': [link_id]},
    ]
    sound = build_node(
        SAVE_AUDIO_ID,
        'SaveAudioAdvanced',
        native_widget_values('SaveAudioAdvanced', native['SaveAudioAdvanced'], f'audio/reactor/{example.slug}'),
        title=NODES['saveAudio'],
    )
    sound['inputs'] = [build_input('audio', 'AUDIO', link_id)]
    sound['outputs'] = [{'name': 'audio', 'type': 'AUDIO', 'links': []}]
    links.append([link_id, GENERATION_ID, 1, SAVE_AUDIO_ID, 0, 'AUDIO'])
    nodes.append(sound)


def append_prompt_sequence(
    example: Example, nodes: list[Json], links: list[Json], generation: dict[str, Json], schemas: dict[str, Json]
) -> None:
    """Add the example's prompt sequence and its connections.

    Args:
        example: The example, whose sources decide the position of the sequence input.
        nodes: The node list that receives both prompt nodes.
        links: The link list that receives the sequence links.
        generation: The generation node, which receives the sequence input.
        schemas: The Reactor node schemas, which hold the prompt node.

    """
    first_link = len(links) + 1
    second_link = first_link + 1
    first = build_node(
        FIRST_STEP_ID,
        'ReactorIncHeliosAddPrompt',
        widget_values(
            schemas['ReactorIncHeliosAddPrompt'],
            {'previous': '[]', 'chunk': 1, 'prompt': SEQUENCE_PROMPTS['sunlight']},
        ),
        title=NODES['sunlight'],
    )
    first['outputs'] = [{'name': 'sequence', 'type': 'STRING', 'links': [first_link]}]
    second = build_node(
        SECOND_STEP_ID,
        'ReactorIncHeliosAddPrompt',
        widget_values(
            schemas['ReactorIncHeliosAddPrompt'],
            {'previous': '[]', 'chunk': 3, 'prompt': SEQUENCE_PROMPTS['clearing']},
        ),
        title=NODES['clearing'],
    )
    second['inputs'] = [build_input('previous', 'STRING', first_link, has_widget=True)]
    second['outputs'] = [{'name': 'sequence', 'type': 'STRING', 'links': [second_link]}]
    incoming: list[Json] = [build_input('image', 'IMAGE', 2)] if ('image' in example.sources) else []
    incoming.append(build_input('sequence', 'STRING', second_link, has_widget=True))
    generation['inputs'] = incoming
    links.extend(
        [
            [first_link, FIRST_STEP_ID, 0, SECOND_STEP_ID, 0, 'STRING'],
            [second_link, SECOND_STEP_ID, 0, GENERATION_ID, len(incoming) - 1, 'STRING'],
        ]
    )
    nodes.extend([first, second])
