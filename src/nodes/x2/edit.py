"""Expose X2 editing through native video and optional image sockets."""

from typing import override
import asyncio
from pathlib import Path
from functools import partial
from dataclasses import replace

import folder_paths
from comfy_api.latest import Input, io

from ..base import VideoNode
from ...runtime import get_runtime
from ..controls import build_inputs, build_outputs
from ...config.nodes import (
    MAX_DURATION_SECONDS,
    MAX_POINTER_POSITION,
    MIN_DURATION_SECONDS,
    MIN_POINTER_POSITION,
    STEP_DURATION_SECONDS,
    STEP_POINTER_POSITION,
    DEFAULT_DURATION_SECONDS,
    DEFAULT_POINTER_POSITION,
)
from ...media.images import encode_png
from ...media.output import owned_io
from ...settings.store import read_settings
from ...comfy.execution import generate_video, wait_for_execution
from ...media.video.input import prepared_video
from ...state.generation.x2 import X2Request
from ...execution.x2.operation import X2Operation


class X2EditVideo(VideoNode):
    """Edit a local video using a prompt, an optional subject image, and a pointer position."""

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows.

        Returns:
            The schema of the node.

        """
        return io.Schema(
            node_id='ReactorIncX2EditVideo',
            display_name='X2: Edit Video (Reactor)',
            description='Edit a local video with a prompt, an optional reference image, and pointer controls.',
            category='Reactor/Edit',
            search_aliases=['Reactor', 'X2', 'video to video', 'reference'],
            inputs=build_inputs(
                'edit',
                leading=[
                    io.Video.Input(
                        'source',
                        display_name='source video',
                        tooltip='Connect one local SDR clip of at least 33 frames.',
                    ),
                ],
                duration=io.Float.Input(
                    'duration_seconds',
                    display_name='video duration (seconds)',
                    default=DEFAULT_DURATION_SECONDS,
                    min=MIN_DURATION_SECONDS,
                    max=MAX_DURATION_SECONDS,
                    step=STEP_DURATION_SECONDS,
                ),
                trailing=[
                    io.Boolean.Input(
                        'keep_backlog',
                        display_name='keep queued frames',
                        default=False,
                        tooltip='Keep source frames in order. This can increase output delay.',
                    ),
                    *_pointer_inputs(),
                    io.Image.Input(
                        'reference_image',
                        display_name='reference image',
                        optional=True,
                        tooltip='Optional single RGB image of the subject to insert or replace.',
                    ),
                ],
                prompt_tooltip='Describe the edit in 1 to 1,000 characters.',
                has_seed=False,
                is_live=True,
            ),
            outputs=build_outputs(has_audio=False),
        )

    @classmethod
    @override
    async def generate(
        cls,
        *,
        source: Input.Video,
        prompt: str,
        duration_seconds: float,
        keep_backlog: bool,
        pointer_active: bool,
        pointer_x: float,
        pointer_y: float,
        reference_image: Input.Image | None = None,
        interactive: bool = False,
    ) -> io.NodeOutput:
        """Edit the source video with X2 and optional reference-image or live controls.

        Args:
            source: The video to edit.
            prompt: The edit prompt.
            duration_seconds: The requested output length in seconds.
            keep_backlog: Whether to keep queued source frames in order.
            pointer_active: Whether to hold the pointer while recording.
            pointer_x: The horizontal position of the pointer.
            pointer_y: The vertical position of the pointer.
            reference_image: The optional image of the subject to insert or replace.
            interactive: Whether to open the live controls.

        Returns:
            The edited video.

        """
        request = X2Request(
            prompt,
            duration_seconds,
            0,
            keep_backlog=keep_backlog,
            pointer_active=pointer_active,
            pointer_x=pointer_x,
            pointer_y=pointer_y,
        )

        async def edit() -> io.NodeOutput:
            """Encode the reference image, then prepare the source frames within the input limits and close them.

            Returns:
                The output of the session.

            """
            settings = await asyncio.to_thread(read_settings, get_runtime().configuration.directory)
            image = None if reference_image is None else await owned_io(partial(encode_png, reference_image))
            async with prepared_video(source, settings, Path(folder_paths.get_temp_directory())) as video:
                return await generate_video(
                    X2Operation(replace(request, image=image, video=video)),
                    interactive=interactive,
                )

        return await wait_for_execution(asyncio.create_task(edit()))


def _pointer_inputs() -> list[io.Input]:
    """Choose whether to hold the pointer, and where to place it on each axis.

    Returns:
        The hold input, then the position input of each axis.

    """
    hold = io.Boolean.Input(
        'pointer_active',
        display_name='hold pointer',
        default=False,
        tooltip='Hold the pointer at the chosen position while recording.',
    )
    positions = [
        io.Float.Input(
            f'pointer_{axis}',
            display_name=f'pointer {axis} (0-1)',
            tooltip=tooltip,
            default=DEFAULT_POINTER_POSITION,
            min=MIN_POINTER_POSITION,
            max=MAX_POINTER_POSITION,
            step=STEP_POINTER_POSITION,
        )
        for axis, tooltip in (
            ('x', '0 is the left edge; 1 is the right edge.'),
            ('y', '0 is the top edge; 1 is the bottom edge.'),
        )
    ]
    return [hold, *positions]
