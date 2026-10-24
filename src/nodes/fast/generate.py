"""Expose a queued Fast H3 clip through native ComfyUI media sockets."""

from typing import override
import asyncio
from functools import partial

from comfy_api.latest import Input, io

from ..base import VideoNode
from ..controls import build_inputs, build_outputs
from ...media.images import encode_png
from ...media.output import owned_io
from ...comfy.execution import generate_video, wait_for_execution
from ...state.generation.fast import FastGenerateRequest
from ...config.generation.fast import (
    DEFAULT_ASPECT,
    OPTIONS_ASPECT,
    MAX_CLIP_SECONDS,
    MIN_CLIP_SECONDS,
    STEP_CLIP_SECONDS,
    DEFAULT_CLIP_SECONDS,
)
from ...execution.fast.generate import FastGenerateOperation


class FastGenerate(VideoNode):
    """Generate one clip, wait for readiness, and save its playback with sound."""

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        duration = io.Float.Input(
            'duration_seconds',
            display_name='video duration (seconds)',
            tooltip=('Fast H3 chooses a supported clip length near this value.'),
            default=DEFAULT_CLIP_SECONDS,
            min=MIN_CLIP_SECONDS,
            max=MAX_CLIP_SECONDS,
            step=STEP_CLIP_SECONDS,
        )
        return io.Schema(
            node_id='ReactorIncFastGenerate',
            display_name='Fast H3: Generate Video (Reactor)',
            category='Reactor/Generate',
            description='Generate a video clip with sound and optional first and last images.',
            search_aliases=['Reactor', 'Fast H3', 'FastH3', 'audio'],
            inputs=build_inputs(
                'fast',
                duration=duration,
                trailing=[
                    io.Combo.Input(
                        'aspect', display_name='aspect ratio', options=OPTIONS_ASPECT, default=DEFAULT_ASPECT
                    ),
                    io.Image.Input(
                        'image',
                        display_name='starting image',
                        optional=True,
                        tooltip='Optional first frame. Connect Load Image.',
                    ),
                    io.Image.Input(
                        'ending_image',
                        display_name='final image',
                        optional=True,
                        tooltip='Optional last frame. Can be used with or without a first frame.',
                    ),
                ],
            ),
            outputs=build_outputs(has_audio=True),
        )

    @classmethod
    @override
    async def generate(
        cls,
        *,
        prompt: str,
        duration_seconds: float,
        seed: int,
        aspect: str,
        image: Input.Image | None = None,
        ending_image: Input.Image | None = None,
    ) -> io.NodeOutput:
        """Generate a Fast H3 video with optional starting and ending images."""

        async def start() -> io.NodeOutput:
            """Prepare media inside the owned task before starting the Reactor session."""
            first = await owned_io(partial(encode_png, image)) if image is not None else None
            last = await owned_io(partial(encode_png, ending_image)) if ending_image is not None else None
            request = FastGenerateRequest(prompt, duration_seconds, seed, image=first, aspect=aspect, ending_image=last)
            return await generate_video(FastGenerateOperation(request))

        return await wait_for_execution(asyncio.create_task(start()))
