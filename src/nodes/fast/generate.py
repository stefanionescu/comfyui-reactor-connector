"""Expose a queued Fast H3 clip through native ComfyUI media sockets."""

import asyncio
from functools import partial
from ...media.output import owned_io
from ...media.images import image_png
from comfy_api.latest import io, Input
from ..controls import generation_controls
from ....config.prompts import FAST_GENERATE_PROMPT
from ...execution.fast.generate import FastGenerateRequest
from ..host import execute_video, wait_for_execution, operation_fingerprint
from ....config.generation.fast import (
    DEFAULT_ASPECT,
    OPTIONS_ASPECT,
    MAX_CLIP_SECONDS,
    MIN_CLIP_SECONDS,
    STEP_CLIP_SECONDS,
    DEFAULT_CLIP_SECONDS,
)


class FastGenerate(io.ComfyNode):
    """Build one clip, wait for readiness, and save its playback with sound."""

    @classmethod
    async def fingerprint_inputs(cls, **_kwargs: object) -> str:
        """Include current settings and model metadata in the ComfyUI cache key."""
        return await operation_fingerprint("fast-queued-recording-v1")

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Declare the saved input names, controls, and output sockets for this node."""
        controls = generation_controls(FAST_GENERATE_PROMPT)
        controls[1] = io.Float.Input(
            "duration_seconds",
            display_name="Video length (seconds)",
            default=DEFAULT_CLIP_SECONDS,
            min=MIN_CLIP_SECONDS,
            max=MAX_CLIP_SECONDS,
            step=STEP_CLIP_SECONDS,
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
                    options=OPTIONS_ASPECT,
                    default=DEFAULT_ASPECT,
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
            description=("Generate a video clip with sound. Help explains clip lengths, images, and saving."),
            search_aliases=["Reactor", "Fast H3", "FastH3", "audio"],
        )

    @classmethod
    async def execute(  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.  # noqa: PLR0913 -- reason: ComfyUI requires one named argument for each saved node input.
        cls,
        *,
        prompt: str,
        duration_seconds: float,
        seed: int,
        variation: int,
        aspect: str,
        image: Input.Image | None = None,
        ending_image: Input.Image | None = None,
    ) -> io.NodeOutput:
        """Generate a Fast H3 video with optional starting and ending images."""
        # ComfyUI uses variation to invalidate its cache; Reactor does not consume it.
        del variation

        async def generate() -> io.NodeOutput:
            """Prepare media inside the owned task before starting the Reactor session."""
            first = await owned_io(partial(image_png, image)) if image is not None else None
            last = await owned_io(partial(image_png, ending_image)) if ending_image is not None else None
            return await execute_video(
                FastGenerateRequest(prompt, duration_seconds, seed, image=first, aspect=aspect, ending_image=last),
                node_id=cls.define_schema().node_id,
            )

        return await wait_for_execution(asyncio.create_task(generate()))
