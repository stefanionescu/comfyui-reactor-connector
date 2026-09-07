"""Expose X2 editing through native video and optional image sockets."""

import asyncio
import folder_paths
from pathlib import Path
from dataclasses import replace
from ...runtime import get_runtime
from ...media.output import owned_io
from ...execution.x2 import X2Request
from ...media.images import image_png
from comfy_api.latest import io, Input
from ...settings.store import read_settings
from ...media.video.input import prepared_video
from ....config.prompts import DEFAULT_EDIT_PROMPT
from ..controls import live_control, video_outputs
from ..host import execute_video, wait_for_execution, operation_fingerprint
from ....config.nodes import (
    MAX_VARIATION,
    MAX_DURATION_SECONDS,
    MIN_DURATION_SECONDS,
    STEP_DURATION_SECONDS,
    STEP_POINTER_POSITION,
    DEFAULT_DURATION_SECONDS,
    DEFAULT_POINTER_POSITION,
)


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
            display_name="Pointer X",
            default=DEFAULT_POINTER_POSITION,
            min=0.0,
            max=1.0,
            step=STEP_POINTER_POSITION,
        ),
        io.Float.Input(
            "pointer_y",
            display_name="Pointer Y",
            default=DEFAULT_POINTER_POSITION,
            min=0.0,
            max=1.0,
            step=STEP_POINTER_POSITION,
        ),
    ]


class X2EditVideo(io.ComfyNode):
    """Edit a local video using a prompt, an optional subject image, and a pointer position."""

    @classmethod
    async def fingerprint_inputs(cls, **_kwargs: object) -> str:
        """Include current settings and model metadata in the ComfyUI cache key."""
        return await operation_fingerprint("x2-source-v1")

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Declare the saved input names, controls, and output sockets for this node."""
        return io.Schema(
            node_id="ReactorIncX2EditVideo",
            display_name="Reactor X2: Edit video",
            category="Reactor/Edit",
            inputs=[
                io.Video.Input(
                    "source",
                    display_name="Source video",
                    tooltip="Connect one local SDR clip of at least 33 frames.",
                ),
                io.String.Input(
                    "prompt",
                    display_name="Scene prompt",
                    placeholder="Scene prompt",
                    multiline=True,
                    default=DEFAULT_EDIT_PROMPT,
                    tooltip="Describe the edit in 1 to 1,000 characters.",
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
                    display_name="Variation",
                    default=0,
                    min=0,
                    max=MAX_VARIATION,
                    tooltip="Change this value to request another paid run.",
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
            description="Edit a local clip. Help explains X2 references and pointer controls.",
            search_aliases=["Reactor", "X2", "video to video", "reference"],
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
    image = None if reference_image is None else await owned_io(lambda: image_png(reference_image))
    async with prepared_video(source, settings, Path(folder_paths.get_temp_directory())) as video:
        return await execute_video(
            replace(request, image=image, video=video),
            interactive=interactive,
            node_id=node_id,
        )
