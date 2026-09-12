"""Expose X2 editing through native video and optional image sockets."""

import asyncio
import folder_paths
from pathlib import Path
from dataclasses import replace
from ...runtime import get_runtime
from ...media.output import owned_io
from ...media.images import encode_png
from comfy_api.latest import io, Input
from ...settings.store import read_settings
from ...state.generation.x2 import X2Request
from ...media.video.input import prepared_video
from ...execution.x2.operation import X2Operation
from ..controls import live_control, video_outputs
from ....config.generation.prompts import DEFAULT_PROMPTS
from ...comfy.execution import generate_video, wait_for_execution, operation_fingerprint
from ....config.nodes import (
    MAX_VARIATION,
    MIN_VARIATION,
    DEFAULT_VARIATION,
    MAX_DURATION_SECONDS,
    MAX_POINTER_POSITION,
    MIN_DURATION_SECONDS,
    MIN_POINTER_POSITION,
    STEP_DURATION_SECONDS,
    STEP_POINTER_POSITION,
    DEFAULT_DURATION_SECONDS,
    DEFAULT_POINTER_POSITION,
)


class X2EditVideo(io.ComfyNode):
    """Edit a local video using a prompt, an optional subject image, and a pointer position."""

    @classmethod
    async def fingerprint_inputs(cls, **_kwargs: object) -> str:
        """Include the operation revision and private configuration token in the cache key."""
        return await operation_fingerprint("x2-source-v1")

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return io.Schema(
            node_id="ReactorIncX2EditVideo",
            display_name="X2: Edit Video (Reactor)",
            description="Edit a local video with a prompt, an optional reference image, and pointer controls.",
            category="Reactor/Edit",
            search_aliases=["Reactor", "X2", "video to video", "reference"],
            inputs=[
                io.Video.Input(
                    "source",
                    display_name="Source video",
                    tooltip="Connect one local SDR clip of at least 33 frames.",
                ),
                io.String.Input(
                    "prompt",
                    display_name="Edit prompt",
                    placeholder="Edit prompt",
                    tooltip="Describe the edit in 1 to 1,000 characters.",
                    multiline=True,
                    default=DEFAULT_PROMPTS["edit"],
                ),
                io.Float.Input(
                    "duration_seconds",
                    display_name="Video length (seconds)",
                    default=DEFAULT_DURATION_SECONDS,
                    min=MIN_DURATION_SECONDS,
                    max=MAX_DURATION_SECONDS,
                    step=STEP_DURATION_SECONDS,
                ),
                io.Int.Input(
                    "variation",
                    display_name="Run number",
                    tooltip="Change this number to run again with unchanged inputs.",
                    default=DEFAULT_VARIATION,
                    min=MIN_VARIATION,
                    max=MAX_VARIATION,
                ),
                io.Boolean.Input(
                    "keep_backlog",
                    display_name="Keep queued frames",
                    default=False,
                    tooltip="Keep source frames in order. This can increase output delay.",
                ),
                *pointer_controls(),
                io.Image.Input(
                    "reference_image",
                    display_name="Reference image",
                    optional=True,
                    tooltip="Optional single RGB image of the subject to insert or replace.",
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
        variation: int,
        keep_backlog: bool,
        pointer_active: bool,
        pointer_x: float,
        pointer_y: float,
        reference_image: Input.Image | None = None,
        interactive: bool = False,
    ) -> io.NodeOutput:
        """Edit the source video with X2 and optional reference-image or live controls."""
        # ComfyUI uses variation to invalidate its cache; Reactor does not consume it.
        del variation
        task = asyncio.create_task(
            _edit(
                X2Request(
                    prompt,
                    duration_seconds,
                    0,
                    keep_backlog=keep_backlog,
                    pointer_active=pointer_active,
                    pointer_x=pointer_x,
                    pointer_y=pointer_y,
                ),
                source,
                reference_image,
                interactive=interactive,
                node_id=cls.define_schema().node_id,
            ),
        )
        return await wait_for_execution(task)


def pointer_controls() -> list[io.Input]:
    """Choose whether to hold the pointer and where to place it."""
    return [
        io.Boolean.Input(
            "pointer_active",
            display_name="Hold pointer",
            default=False,
            tooltip="Hold the pointer at the chosen position while recording.",
        ),
        io.Float.Input(
            "pointer_x",
            display_name="Horizontal position (0-1)",
            tooltip="0 is the left edge; 1 is the right edge.",
            default=DEFAULT_POINTER_POSITION,
            min=MIN_POINTER_POSITION,
            max=MAX_POINTER_POSITION,
            step=STEP_POINTER_POSITION,
        ),
        io.Float.Input(
            "pointer_y",
            display_name="Vertical position (0-1)",
            tooltip="0 is the top edge; 1 is the bottom edge.",
            default=DEFAULT_POINTER_POSITION,
            min=MIN_POINTER_POSITION,
            max=MAX_POINTER_POSITION,
            step=STEP_POINTER_POSITION,
        ),
    ]


async def _edit(
    request: X2Request,
    source: Input.Video,
    reference_image: Input.Image | None,
    *,
    interactive: bool,
    node_id: str,
) -> io.NodeOutput:
    """Prepare source frames within the input limits and close them after the edit."""
    settings = await asyncio.to_thread(read_settings, get_runtime().configuration.directory)
    image = None if reference_image is None else await owned_io(lambda: encode_png(reference_image))
    async with prepared_video(source, settings, Path(folder_paths.get_temp_directory())) as video:
        return await generate_video(
            X2Operation(replace(request, image=image, video=video)),
            interactive=interactive,
            node_id=node_id,
        )
