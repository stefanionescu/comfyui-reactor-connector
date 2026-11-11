"""Expose SANA file editing with native ComfyUI video input and output."""

from typing import override
import asyncio
from pathlib import Path
from dataclasses import replace

import folder_paths
from comfy_api.latest import Input, io

from ..base import VideoNode
from ...runtime import get_runtime
from ..controls import build_inputs, build_outputs
from ...settings.store import read_settings
from ...comfy.execution import generate_video, wait_for_execution
from ...media.video.input import prepared_video
from ...state.generation.sana import SanaRequest
from ...config.generation.video import MAX_ANCHOR_INTERVAL, MIN_ANCHOR_INTERVAL, DEFAULT_ANCHOR_INTERVAL
from ...execution.sana.operation import SanaOperation


class SanaEditVideo(VideoNode):
    """Apply a written edit to a video clip."""

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows.

        Returns:
            The schema of the node.

        """
        return io.Schema(
            node_id='ReactorIncSanaEditVideo',
            display_name='SANA: Edit Video (Reactor)',
            description='Edit a video from your computer using a text prompt. Choose the output length.',
            category='Reactor/Edit',
            search_aliases=['Reactor', 'SANA', 'video to video', 'edit'],
            inputs=build_inputs(
                'edit',
                leading=[
                    io.Video.Input(
                        'source',
                        display_name='source video',
                        tooltip='Connect one local SDR clip with at least 33 frames.',
                    ),
                ],
                trailing=[
                    io.Int.Input(
                        'anchor_interval',
                        display_name='source refresh interval (chunks)',
                        tooltip='Return to the source image after this many model chunks. Use 0 to turn this off.',
                        default=DEFAULT_ANCHOR_INTERVAL,
                        min=MIN_ANCHOR_INTERVAL,
                        max=MAX_ANCHOR_INTERVAL,
                    ),
                ],
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
        seed: int,
        anchor_interval: int,
        interactive: bool = False,
    ) -> io.NodeOutput:
        """Edit the source video with SANA and return the recorded result.

        Args:
            source: The video to edit.
            prompt: The edit prompt.
            duration_seconds: The requested output length in seconds.
            seed: The seed that the model generates from.
            anchor_interval: The number of model chunks between returns to the source image.
            interactive: Whether to open the live controls.

        Returns:
            The edited video.

        """
        request = SanaRequest(prompt, duration_seconds, seed, anchor_interval=anchor_interval)

        async def edit() -> io.NodeOutput:
            """Prepare the source frames within the input limits, and close them after the edit.

            Returns:
                The output of the session.

            """
            settings = await asyncio.to_thread(read_settings, get_runtime().configuration.directory)
            async with prepared_video(source, settings, Path(folder_paths.get_temp_directory())) as video:
                return await generate_video(
                    SanaOperation(replace(request, video=video)),
                    interactive=interactive,
                )

        return await wait_for_execution(asyncio.create_task(edit()))
