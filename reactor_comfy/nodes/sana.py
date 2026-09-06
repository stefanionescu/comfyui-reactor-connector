"""Expose SANA file editing with native ComfyUI video input and output."""

import asyncio
from pathlib import Path

import folder_paths
from comfy_api.latest import Input, io

from ..config_store import load_settings
from ..execution.sana import SanaRequest
from ..media.video_input import prepared_video
from ..runtime import get_runtime
from .controls import generation_controls, live_control, video_outputs
from .host import execute_video, operation_fingerprint, wait_for_execution


class SanaEditVideo(io.ComfyNode):
    """Apply a written edit to a video clip."""

    @classmethod
    async def fingerprint_inputs(cls, **kwargs: object) -> str:
        return await operation_fingerprint("sana-source-v2")

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="ReactorIncSanaEditVideo",
            display_name="Reactor SANA: Edit video",
            category="Reactor/Edit",
            inputs=[
                io.Video.Input(
                    "source",
                    display_name="Source video",
                    tooltip="Connect one local SDR clip with at least 33 frames.",
                ),
                *generation_controls("Change the scene to a soft watercolor painting."),
                io.Int.Input(
                    "anchor_interval",
                    display_name="Anchor interval",
                    default=0,
                    min=0,
                    max=1000,
                    tooltip=(
                        "Return to the source image after this many model chunks. Use 0 "
                        "to turn this off."
                    ),
                ),
                live_control(),
            ],
            outputs=video_outputs(),
            description=(
                "Edit a video from your computer using a text prompt. Choose the output length."
            ),
            search_aliases=["Reactor", "SANA", "video to video", "edit"],
        )

    @classmethod
    async def execute(
        cls,
        source: Input.Video,
        prompt: str,
        duration_seconds: float,
        seed: int,
        variation: int,
        anchor_interval: int,
        interactive: bool = False,
    ) -> io.NodeOutput:
        task = asyncio.create_task(
            _edit(
                source,
                prompt,
                duration_seconds,
                seed,
                anchor_interval,
                interactive,
                node_id=cls.define_schema().node_id,
            )
        )
        return await wait_for_execution(task)


async def _edit(
    source: Input.Video,
    prompt: str,
    duration_seconds: float,
    seed: int,
    anchor_interval: int,
    interactive: bool,
    *,
    node_id: str,
) -> io.NodeOutput:
    settings = await asyncio.to_thread(load_settings, get_runtime().configuration.directory)
    async with prepared_video(source, settings, Path(folder_paths.get_temp_directory())) as video:
        return await execute_video(
            SanaRequest(
                prompt,
                duration_seconds,
                seed,
                video=video,
                anchor_interval=anchor_interval,
            ),
            interactive=interactive,
            node_id=node_id,
        )
