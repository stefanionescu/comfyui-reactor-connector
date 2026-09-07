"""Record edits from a camera explicitly enabled in the owning browser."""

import asyncio
from functools import partial
from ...media.output import owned_io
from ..controls import video_outputs
from ...execution.x2 import X2Request
from ...media.images import image_png
from comfy_api.latest import io, Input
from ...media.webcam import WebcamFrames
from ...live.control.lease import LiveOptions
from ....config.prompts import DEFAULT_WEBCAM_PROMPT
from ..host import execute_video, wait_for_execution, operation_fingerprint
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
        """Declare the saved input names, controls, and output sockets for this node."""
        return io.Schema(
            node_id="ReactorIncX2Webcam",
            display_name="Reactor X2: Edit a webcam",
            category="Reactor/Live",
            inputs=[
                io.String.Input(
                    "prompt",
                    display_name="Scene prompt",
                    placeholder="Scene prompt",
                    multiline=True,
                    default=DEFAULT_WEBCAM_PROMPT,
                ),
                io.Float.Input(
                    "duration_seconds",
                    display_name="Video length (seconds)",
                    default=DEFAULT_WEBCAM_SECONDS,
                    min=MIN_WEBCAM_SECONDS,
                    max=MAX_WEBCAM_SECONDS,
                    step=STEP_WEBCAM_SECONDS,
                ),
                io.Int.Input(
                    "variation",
                    display_name="Variation",
                    default=0,
                    min=0,
                    max=MAX_VARIATION,
                    tooltip="Change this value to request another paid run.",
                ),
                io.Image.Input(
                    "reference_image",
                    display_name="Reference image",
                    optional=True,
                    tooltip="Optional picture of a subject to insert or replace.",
                ),
            ],
            outputs=video_outputs(),
            description="Edit webcam video and drag on the output to steer the subject.",
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
