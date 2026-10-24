"""Describe X2 workflow inputs and controls."""

from ..live import build_live_example
from ..example import Example

# The pointer and backlog settings that both file edit examples keep at their defaults.
_EDIT_CONTROLS: dict[str, str | float | bool] = {
    'duration_seconds': 5.0,
    'variation': 0,
    'keep_backlog': False,
    'pointer_active': False,
    'pointer_x': 0.5,
    'pointer_y': 0.5,
    'interactive': False,
}

EXAMPLES = (
    Example(
        'x2-01-edit-video',
        'ReactorIncX2EditVideo',
        model='x2',
        inputs={
            'prompt': 'Change the scene to a soft watercolor painting. Keep the movement and composition.',
            **_EDIT_CONTROLS,
        },
        sources=('source',),
    ),
    Example(
        'x2-02-reference-edit',
        'ReactorIncX2EditVideo',
        model='x2',
        inputs={
            'prompt': 'Replace the main subject with the subject from the reference image. Keep the background.',
            **_EDIT_CONTROLS,
        },
        sources=('source', 'reference_image'),
    ),
    Example(
        'x2-03-webcam',
        'ReactorIncX2Webcam',
        model='x2',
        inputs={'prompt': 'Turn the scene into a watercolor painting.', 'duration_seconds': 20, 'variation': 0},
        mode='webcam',
    ),
)


LIVE_EXAMPLES = (build_live_example(EXAMPLES[0], 'x2-04-live-prompt'),)
