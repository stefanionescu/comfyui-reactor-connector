"""Build live examples from a model's recorded examples."""

from dataclasses import replace

from .example import Example


def build_live_example(example: Example, slug: str, *, prompt: str | None = None) -> Example:
    """Keep recorded inputs while enabling live controls and an optional opening prompt."""
    inputs = example.inputs | {'duration_seconds': 20, 'interactive': True}
    if prompt is not None:
        inputs['prompt'] = prompt
    return replace(example, slug=slug, inputs=inputs, mode='live')
