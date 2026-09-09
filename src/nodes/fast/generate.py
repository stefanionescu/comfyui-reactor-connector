"""Expose a queued Fast H3 clip through native ComfyUI media sockets."""

import asyncio
from functools import partial
from ...media.output import owned_io
from ...media.images import image_png
from ..schema import translate_schema
from comfy_api.latest import io, Input
from ..controls import generation_controls
from ...execution.fast.generate import FastGenerateRequest
from ...comfy.execution import execute_video, wait_for_execution, operation_fingerprint
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
        """Define the inputs and outputs saved in ComfyUI workflows."""
        controls = generation_controls("fast")
        controls[1] = io.Float.Input(
            "duration_seconds",
            default=DEFAULT_CLIP_SECONDS,
            min=MIN_CLIP_SECONDS,
            max=MAX_CLIP_SECONDS,
            step=STEP_CLIP_SECONDS,
        )
        return translate_schema(
            io.Schema(
                node_id="ReactorIncFastGenerate",
                inputs=[
                    *controls,
                    io.Combo.Input(
                        "aspect",
                        options=OPTIONS_ASPECT,
                        default=DEFAULT_ASPECT,
                    ),
                    io.Image.Input(
                        "image",
                        optional=True,
                    ),
                    io.Image.Input(
                        "ending_image",
                        optional=True,
                    ),
                ],
                outputs=[
                    io.Video.Output(),
                    io.Audio.Output(),
                    io.String.Output(),
                ],
            )
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
