"""Describe LongLive workflow inputs and controls."""

from ..live import build_live_example
from ..example import Example

SHOT_PROMPTS = {
    'soft_transition': 'The camera pulls back to show the trees around the fox.',
    'hard_cut': 'A wide view of a still lake at sunrise.',
}

# The storyboard example adds its shots through plan nodes, so it starts from the same inputs.
_INPUTS: dict[str, str | float | bool] = {
    'prompt': 'A fox walks along a forest path. The camera follows slowly.',
    'duration_seconds': 5.0,
    'variation': 0,
    'seed': 42,
    'control_after_generate': 'fixed',
    'storyboard': '[]',
    'interactive': False,
}

EXAMPLES = (
    Example('longlive-v2-01-text-to-video', 'ReactorIncLongLiveGenerate', model='longlive-v2', inputs=_INPUTS),
    Example(
        'longlive-v2-02-storyboard', 'ReactorIncLongLiveGenerate', model='longlive-v2', inputs=_INPUTS, plan='shots'
    ),
)


LIVE_EXAMPLES = (build_live_example(EXAMPLES[0], 'longlive-v2-03-live-prompt'),)
