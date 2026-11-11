"""Continue a scene across several clips without queuing another ComfyUI run."""

from typing import override
import asyncio
from functools import partial

from comfy_api.latest import Input, io

from ..base import VideoNode
from ..controls import build_inputs, build_outputs
from ...media.images import encode_png
from ...media.output import owned_io
from ...comfy.execution import generate_video, wait_for_execution
from ...state.generation.fast import FastContinueRequest
from ...config.generation.fast import (
    DEFAULT_ASPECT,
    MAX_CLIP_COUNT,
    MIN_CLIP_COUNT,
    OPTIONS_ASPECT,
    MAX_CLIP_SECONDS,
    MIN_CLIP_SECONDS,
    STEP_CLIP_SECONDS,
    DEFAULT_CLIP_COUNT,
    DEFAULT_CLIP_SECONDS,
)
from ...execution.fast.continuation import FastContinueOperation


class FastContinue(VideoNode):
    """Join a sequence of Fast H3 clips that continue from each previous final frame."""

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows.

        Returns:
            The schema of the node.

        """
        duration = io.Float.Input(
            'clip_seconds',
            display_name='clip duration (seconds)',
            tooltip='Length of each clip. Fast H3 chooses the closest supported length.',
            default=DEFAULT_CLIP_SECONDS,
            min=MIN_CLIP_SECONDS,
            max=MAX_CLIP_SECONDS,
            step=STEP_CLIP_SECONDS,
        )
        return io.Schema(
            node_id='ReactorIncFastContinue',
            display_name='Fast H3: Continue a Scene (Reactor)',
            description='Chain clips from their previous final frame and save one video with sound.',
            category='Reactor/Generate',
            search_aliases=[],
            inputs=build_inputs(
                'continuation',
                duration=duration,
                trailing=[
                    io.Combo.Input(
                        'aspect', display_name='aspect ratio', options=OPTIONS_ASPECT, default=DEFAULT_ASPECT
                    ),
                    io.Int.Input(
                        'clip_count',
                        display_name='number of clips',
                        tooltip='Number of clips in one session. Their combined length must be 60 seconds or less.',
                        default=DEFAULT_CLIP_COUNT,
                        min=MIN_CLIP_COUNT,
                        max=MAX_CLIP_COUNT,
                    ),
                    io.String.Input(
                        'later_prompts',
                        display_name='later clip prompts',
                        placeholder='later clip prompts',
                        tooltip=(
                            'Optional later scenes: one prompt per line, starting with clip 2. '
                            'Empty uses the opening prompt.'
                        ),
                        multiline=True,
                        default='',
                    ),
                    io.Image.Input(
                        'image',
                        display_name='starting image',
                        optional=True,
                        tooltip='Optional first frame for the first clip.',
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
        clip_seconds: float,
        seed: int,
        aspect: str,
        clip_count: int,
        later_prompts: str,
        image: Input.Image | None = None,
    ) -> io.NodeOutput:
        """Join a sequence of Fast H3 clips that continue from each previous final frame.

        Args:
            prompt: The prompt of the first clip.
            clip_seconds: The length of each clip in seconds.
            seed: The seed that the model generates from.
            aspect: The aspect ratio of the video.
            clip_count: The number of clips to join.
            later_prompts: The prompts of the later clips, one per line.
            image: The optional first frame of the first clip.

        Returns:
            The joined video and its sound.

        """

        async def start() -> io.NodeOutput:
            """Prepare media inside the owned task before starting the Reactor session.

            Returns:
                The output of the session.

            """
            encoded = None if image is None else await owned_io(partial(encode_png, image))
            request = FastContinueRequest(
                prompt,
                clip_seconds * clip_count,
                seed,
                image=encoded,
                aspect=aspect,
                clip_seconds=clip_seconds,
                clip_count=clip_count,
                later_prompts=tuple(later_prompts.splitlines()),
            )
            return await generate_video(FastContinueOperation(request))

        return await wait_for_execution(asyncio.create_task(start()))
