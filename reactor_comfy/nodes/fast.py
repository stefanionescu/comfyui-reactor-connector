"""Expose a queued Fast H3 clip through native ComfyUI media sockets."""

import asyncio
from functools import partial

from comfy_api.latest import Input, io

from ..execution.fast import FastGenerateRequest
from ..media.file_output import owned_io
from ..media.images import image_png
from .controls import generation_controls
from .host import execute_video, operation_fingerprint, wait_for_execution


class FastGenerate(io.ComfyNode):
    """Build one clip, wait for readiness, and save its playback with sound."""

    @classmethod
    async def fingerprint_inputs(cls, **kwargs: object) -> str:
        return await operation_fingerprint("fast-queued-recording-v1")

    @classmethod
    def define_schema(cls) -> io.Schema:
        controls = generation_controls(
            "A small stream flows over smooth stones. Water splashes softly and birds call."
        )
        controls[1] = io.Float.Input(
            "duration_seconds",
            display_name="Video length (seconds)",
            default=6.0,
            min=5.167,
            max=14.375,
            step=0.001,
            tooltip=(
                "Fast H3 chooses a supported clip length near this value. "
                "The clip must fit the video duration limit in Reactor settings."
            ),
        )
        return io.Schema(
            node_id="ReactorIncFastGenerate",
            display_name="Reactor Fast H3: Generate video",
            category="Reactor/Generate",
            inputs=[
                *controls,
                io.Combo.Input(
                    "aspect",
                    display_name="Aspect ratio",
                    options=["16:9", "1:1", "9:16", "4:3"],
                    default="16:9",
                ),
                io.Image.Input(
                    "image",
                    display_name="Starting image",
                    optional=True,
                    tooltip="Optional first frame. Connect Load Image.",
                ),
                io.Image.Input(
                    "ending_image",
                    display_name="Final image",
                    optional=True,
                    tooltip="Optional last frame. Can be used with or without a first frame.",
                ),
            ],
            outputs=[
                io.Video.Output(display_name="video"),
                io.Audio.Output(display_name="audio"),
                io.String.Output(display_name="metadata"),
            ],
            description=(
                "Generate a video clip with sound. Help explains clip lengths, images, and saving."
            ),
            search_aliases=["Reactor", "Fast H3", "FastH3", "audio"],
        )

    @classmethod
    async def execute(
        cls,
        prompt: str,
        duration_seconds: float,
        seed: int,
        variation: int,
        aspect: str,
        image: Input.Image | None = None,
        ending_image: Input.Image | None = None,
    ) -> io.NodeOutput:
        async def generate() -> io.NodeOutput:
            first = await owned_io(partial(image_png, image)) if image is not None else None
            last = (
                await owned_io(partial(image_png, ending_image))
                if ending_image is not None
                else None
            )
            return await execute_video(
                FastGenerateRequest(
                    prompt, duration_seconds, seed, image=first, aspect=aspect, ending_image=last
                ),
                node_id=cls.define_schema().node_id,
            )

        return await wait_for_execution(asyncio.create_task(generate()))
