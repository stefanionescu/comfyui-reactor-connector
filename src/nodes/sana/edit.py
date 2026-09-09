"""Expose SANA file editing with native ComfyUI video input and output."""

import asyncio
import folder_paths
from pathlib import Path
from dataclasses import replace
from ...runtime import get_runtime
from ..schema import translate_schema
from comfy_api.latest import io, Input
from ...settings.store import read_settings
from ...media.video.input import prepared_video
from ...execution.sana.request import SanaRequest
from ....config.generation.video import MAX_ANCHOR_INTERVAL
from ..controls import live_control, video_outputs, generation_controls
from ...comfy.execution import execute_video, wait_for_execution, operation_fingerprint


class SanaEditVideo(io.ComfyNode):
    """Apply a written edit to a video clip."""

    @classmethod
    async def fingerprint_inputs(cls, **_kwargs: object) -> str:
        """Include current settings and model metadata in the ComfyUI cache key."""
        return await operation_fingerprint("sana-source-v2")

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Declare the saved input names, controls, and output sockets for this node."""
        return translate_schema(
            io.Schema(
                node_id="ReactorIncSanaEditVideo",
                inputs=[
                    io.Video.Input(
                        "source",
                    ),
                    *generation_controls("edit"),
                    io.Int.Input(
                        "anchor_interval",
                        default=0,
                        min=0,
                        max=MAX_ANCHOR_INTERVAL,
                    ),
                    live_control(),
                ],
                outputs=video_outputs(),
            )
        )

    @classmethod
    async def execute(  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.  # noqa: PLR0913 -- reason: ComfyUI requires one named argument for each saved node input.
        cls,
        *,
        source: Input.Video,
        prompt: str,
        duration_seconds: float,
        seed: int,
        variation: int,
        anchor_interval: int,
        interactive: bool = False,
    ) -> io.NodeOutput:
        """Edit the source video with SANA and return the recorded result."""
        # ComfyUI uses variation to invalidate its cache; Reactor does not consume it.
        del variation
        task = asyncio.create_task(
            _edit(
                SanaRequest(prompt, duration_seconds, seed, anchor_interval=anchor_interval),
                source,
                interactive=interactive,
                node_id=cls.define_schema().node_id,
            )
        )
        return await wait_for_execution(task)


async def _edit(
    request: SanaRequest,
    source: Input.Video,
    *,
    interactive: bool,
    node_id: str,
) -> io.NodeOutput:
    """Prepare source frames within the input limits and close them after the edit."""
    settings = await asyncio.to_thread(read_settings, get_runtime().configuration.directory)
    async with prepared_video(source, settings, Path(folder_paths.get_temp_directory())) as video:
        return await execute_video(
            replace(request, video=video),
            interactive=interactive,
            node_id=node_id,
        )
