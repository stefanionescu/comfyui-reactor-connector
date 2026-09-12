"""Expose SANA file editing with native ComfyUI video input and output."""

import asyncio
import folder_paths
from pathlib import Path
from dataclasses import replace
from ...runtime import get_runtime
from comfy_api.latest import io, Input
from ...settings.store import read_settings
from ...media.video.input import prepared_video
from ...state.generation.sana import SanaRequest
from ...execution.sana.operation import SanaOperation
from ..controls import live_control, video_outputs, generation_controls
from ...comfy.execution import generate_video, wait_for_execution, operation_fingerprint
from ....config.generation.video import MAX_ANCHOR_INTERVAL, MIN_ANCHOR_INTERVAL, DEFAULT_ANCHOR_INTERVAL


class SanaEditVideo(io.ComfyNode):
    """Apply a written edit to a video clip."""

    @classmethod
    async def fingerprint_inputs(cls, **_kwargs: object) -> str:
        """Include the operation revision and private configuration token in the cache key."""
        return await operation_fingerprint("sana-source-v2")

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return io.Schema(
            node_id="ReactorIncSanaEditVideo",
            display_name="SANA: Edit Video (Reactor)",
            description="Edit a video from your computer using a text prompt. Choose the output length.",
            category="Reactor/Edit",
            search_aliases=["Reactor", "SANA", "video to video", "edit"],
            inputs=[
                io.Video.Input(
                    "source",
                    display_name="Source video",
                    tooltip="Connect one local SDR clip with at least 33 frames.",
                ),
                *generation_controls("edit"),
                io.Int.Input(
                    "anchor_interval",
                    display_name="Source refresh interval (chunks)",
                    tooltip="Return to the source image after this many model chunks. Use 0 to turn this off.",
                    default=DEFAULT_ANCHOR_INTERVAL,
                    min=MIN_ANCHOR_INTERVAL,
                    max=MAX_ANCHOR_INTERVAL,
                ),
                live_control(),
            ],
            outputs=video_outputs(),
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
        return await generate_video(
            SanaOperation(replace(request, video=video)),
            interactive=interactive,
            node_id=node_id,
        )
