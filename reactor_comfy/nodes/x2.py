"""Expose X2 editing through native video and optional image sockets."""

import asyncio
from pathlib import Path

import folder_paths
from comfy_api.latest import Input, io

from ..config_store import load_settings
from ..execution.x2 import X2Request
from ..media.file_output import owned_io
from ..media.images import image_png
from ..media.video_input import prepared_video
from ..runtime import get_runtime
from .controls import live_control, video_outputs
from .host import execute_video, operation_fingerprint, wait_for_execution


class X2EditVideo(io.ComfyNode):
    """Edit a local video using a prompt, an optional subject image, and a pointer position."""

    @classmethod
    async def fingerprint_inputs(cls, **kwargs: object) -> str:
        return await operation_fingerprint("x2-source-v1")

    @classmethod
    def define_schema(cls) -> io.Schema:
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
                    default="Change the scene to a soft watercolor painting.",
                    tooltip="Describe the edit in 1 to 1,000 characters.",
                ),
                io.Float.Input(
                    "duration_seconds",
                    display_name="Video length (seconds)",
                    default=5.0,
                    min=0.1,
                    max=60.0,
                    step=0.1,
                ),
                io.Int.Input(
                    "variation",
                    display_name="Variation",
                    default=0,
                    min=0,
                    max=2**31 - 1,
                    tooltip="Change this value to request another paid run.",
                ),
                io.Boolean.Input(
                    "keep_backlog",
                    display_name="Keep queued frames",
                    default=False,
                    tooltip="Keep source frames in order. This can increase output delay.",
                ),
                io.Boolean.Input(
                    "pointer_active",
                    display_name="Hold pointer",
                    default=False,
                    tooltip="Hold the pointer at the chosen position while recording.",
                ),
                io.Float.Input(
                    "pointer_x", display_name="Pointer X", default=0.5, min=0.0, max=1.0, step=0.01
                ),
                io.Float.Input(
                    "pointer_y", display_name="Pointer Y", default=0.5, min=0.0, max=1.0, step=0.01
                ),
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
    async def execute(
        cls,
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
        task = asyncio.create_task(
            _edit(
                source,
                prompt,
                duration_seconds,
                keep_backlog,
                pointer_active,
                pointer_x,
                pointer_y,
                reference_image,
                interactive,
                node_id=cls.define_schema().node_id,
            ),
        )
        return await wait_for_execution(task)


async def _edit(
    source: Input.Video,
    prompt: str,
    duration_seconds: float,
    keep_backlog: bool,
    pointer_active: bool,
    pointer_x: float,
    pointer_y: float,
    reference_image: Input.Image | None,
    interactive: bool,
    *,
    node_id: str,
) -> io.NodeOutput:
    settings = await asyncio.to_thread(load_settings, get_runtime().configuration.directory)
    image = None if reference_image is None else await owned_io(lambda: image_png(reference_image))
    async with prepared_video(source, settings, Path(folder_paths.get_temp_directory())) as video:
        return await execute_video(
            X2Request(
                prompt,
                duration_seconds,
                0,
                image=image,
                video=video,
                keep_backlog=keep_backlog,
                pointer_active=pointer_active,
                pointer_x=pointer_x,
                pointer_y=pointer_y,
            ),
            interactive=interactive,
            node_id=node_id,
        )
