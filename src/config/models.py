"""Describe reviewed Reactor model identities and live capabilities."""

from typing import Literal, TypedDict, NotRequired

from .generation.fast import MAX_PROMPT_CHARACTERS as MAX_FAST_PROMPT_CHARACTERS
from .generation.video import MAX_EDIT_PROMPT_CHARACTERS
from .generation.world import LINGBOT_CAMERA_AXES, LINGBOT_WORLD_CAMERA_AXES, MAX_WORLD_PROMPT_CHARACTERS
from .generation.session import MAX_PROMPT_CHARACTERS


class ModelIdentity(TypedDict):
    """One model identity; a field it leaves out takes the default of the model definition record."""

    guide_slug: str
    connection_name: str
    title: str
    max_prompt_characters: int
    prompt_kind: NotRequired[Literal['scene', 'edit']]
    is_empty_prompt_allowed: NotRequired[bool]
    camera_axes: NotRequired[tuple[str, ...]]
    prompt_command: NotRequired[str]
    has_audio_prompt: NotRequired[bool]
    has_pointer: NotRequired[bool]
    has_prompt_passthrough: NotRequired[bool]


MODEL_IDENTITIES: dict[str, ModelIdentity] = {
    'fast-h3': {
        'guide_slug': 'fast-h3',
        'connection_name': 'reactor/fast-h3',
        'title': 'Fast H3',
        'max_prompt_characters': MAX_FAST_PROMPT_CHARACTERS,
    },
    'visko-orbis-stable': {
        'guide_slug': 'visko-orbis-stable',
        'connection_name': 'reactor/visko-orbis-stable',
        'title': 'Visko Stable',
        'max_prompt_characters': MAX_PROMPT_CHARACTERS,
        'has_audio_prompt': True,
        'has_prompt_passthrough': True,
    },
    'visko-orbis-dynamic': {
        'guide_slug': 'visko-orbis-dynamic',
        'connection_name': 'reactor/visko-orbis-dynamic',
        'title': 'Visko Dynamic',
        'max_prompt_characters': MAX_PROMPT_CHARACTERS,
        'has_audio_prompt': True,
        'has_prompt_passthrough': True,
    },
    'helios': {
        'guide_slug': 'helios',
        'connection_name': 'reactor/helios',
        'title': 'Helios',
        'max_prompt_characters': MAX_PROMPT_CHARACTERS,
    },
    'lingbot': {
        'guide_slug': 'lingbot',
        'connection_name': 'reactor/lingbot',
        'title': 'LingBot',
        'max_prompt_characters': MAX_WORLD_PROMPT_CHARACTERS,
        'camera_axes': LINGBOT_CAMERA_AXES,
    },
    'lingbot-world-2': {
        'guide_slug': 'lingbot-world-2',
        'connection_name': 'reactor/lingbot-world-2',
        'title': 'LingBot World 2',
        'max_prompt_characters': MAX_WORLD_PROMPT_CHARACTERS,
        'camera_axes': LINGBOT_WORLD_CAMERA_AXES,
    },
    'longlive-v2': {
        'guide_slug': 'longlive-v2',
        'connection_name': 'reactor/longlive-v2',
        'title': 'LongLive',
        'max_prompt_characters': MAX_PROMPT_CHARACTERS,
        'prompt_command': 'set_shot',
    },
    'sana-streaming': {
        'guide_slug': 'sana-streaming',
        'connection_name': 'reactor/sana-streaming',
        'title': 'SANA',
        'max_prompt_characters': MAX_PROMPT_CHARACTERS,
        'prompt_kind': 'edit',
        'is_empty_prompt_allowed': True,
    },
    'ltx2': {
        'guide_slug': 'ltx',
        'connection_name': 'reactor/ltx2',
        'title': 'LTX',
        'max_prompt_characters': MAX_PROMPT_CHARACTERS,
    },
    'x2': {
        'guide_slug': 'x2',
        'connection_name': 'xmax/x2',
        'title': 'X2',
        'max_prompt_characters': MAX_EDIT_PROMPT_CHARACTERS,
        'prompt_kind': 'edit',
        'has_pointer': True,
    },
}
