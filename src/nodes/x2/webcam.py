"""Record edits from a camera explicitly enabled in the owning browser."""

import asyncio
from functools import partial
from ...media.output import owned_io
from ..controls import video_outputs
from ...live.state import LiveOptions
from ...media.images import image_png
from ..schema import translate_schema
from comfy_api.latest import io, Input
from ...media.webcam import WebcamFrames
from ...execution.x2.request import X2Request
from ....config.generation.prompts import DEFAULT_PROMPTS
from ...comfy.execution import execute_video, wait_for_execution, operation_fingerprint
from ....config.nodes import (
    MAX_VARIATION,
    MAX_WEBCAM_SECONDS,
    MIN_WEBCAM_SECONDS,
    STEP_WEBCAM_SECONDS,
    DEFAULT_WEBCAM_SECONDS,
)


class X2Webcam(io.ComfyNode):
    """Open X2 webcam and dragging controls and record the resulting video."""

    @classmethod
    async def fingerprint_inputs(cls, **_kwargs: object) -> str:
        """Include current settings and model metadata in the ComfyUI cache key."""
        return await operation_fingerprint("x2-webcam-v1")

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return translate_schema(
            io.Schema(
                node_id="ReactorIncX2Webcam",
                inputs=[
                    io.String.Input(
                        "prompt",
                        multiline=True,
                        default=DEFAULT_PROMPTS["webcam"],
                    ),
                    io.Float.Input(
                        "duration_seconds",
                        default=DEFAULT_WEBCAM_SECONDS,
                        min=MIN_WEBCAM_SECONDS,
                        max=MAX_WEBCAM_SECONDS,
                        step=STEP_WEBCAM_SECONDS,
                    ),
                    io.Int.Input(
                        "variation",
                        default=0,
                        min=0,
                        max=MAX_VARIATION,
                    ),
                    io.Image.Input(
                        "reference_image",
                        optional=True,
                    ),
                ],
                outputs=video_outputs(),
            )
        )

    @classmethod
    async def execute(  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        cls,
        *,
        prompt: str,
        duration_seconds: float,
        variation: int,
        reference_image: Input.Image | None = None,
    ) -> io.NodeOutput:
        """Open X2 webcam and dragging controls and record the resulting video."""
        # ComfyUI uses variation to invalidate its cache; Reactor does not consume it.
        del variation

        async def generate() -> io.NodeOutput:
            """Prepare media inside the owned task before starting the Reactor session."""
            camera = WebcamFrames()
            try:
                image = None if reference_image is None else await owned_io(partial(image_png, reference_image))
                request = X2Request(prompt, duration_seconds, 0, image=image, webcam=camera)
                return await execute_video(
                    request,
                    controls=LiveOptions(request.model_name, prompt, camera),
                    node_id=cls.define_schema().node_id,
                )
            finally:
                await camera.close()

        return await wait_for_execution(asyncio.create_task(generate()))
