"""Record edits from a camera explicitly enabled in the owning browser."""

import asyncio
from functools import partial
from ...media.output import owned_io
from ..controls import video_outputs
from ...media.images import encode_png
from comfy_api.latest import io, Input
from ...media.webcam import WebcamFrames
from ...state.generation.x2 import X2Request
from ...execution.x2.operation import X2Operation
from ...comfy.interaction import build_live_options
from ....config.generation.prompts import DEFAULT_PROMPTS
from ...comfy.execution import generate_video, wait_for_execution, operation_fingerprint
from ....config.nodes import (
    MAX_VARIATION,
    MIN_VARIATION,
    DEFAULT_VARIATION,
    MAX_WEBCAM_SECONDS,
    MIN_WEBCAM_SECONDS,
    STEP_WEBCAM_SECONDS,
    DEFAULT_WEBCAM_SECONDS,
    DEFAULT_POINTER_POSITION,
)


class X2Webcam(io.ComfyNode):
    """Open X2 webcam and dragging controls and record the resulting video."""

    @classmethod
    async def fingerprint_inputs(cls, **_kwargs: object) -> str:
        """Include the operation revision and private configuration token in the cache key."""
        return await operation_fingerprint("x2-webcam-v1")

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return io.Schema(
            node_id="ReactorIncX2Webcam",
            display_name="X2: Edit Webcam Video (Reactor)",
            description="Edit webcam video and drag on the output to steer the subject.",
            category="Reactor/Live",
            search_aliases=[],
            inputs=[
                io.String.Input(
                    "prompt",
                    display_name="edit prompt",
                    placeholder="edit prompt",
                    multiline=True,
                    default=DEFAULT_PROMPTS["webcam"],
                ),
                io.Float.Input(
                    "duration_seconds",
                    display_name="video duration (seconds)",
                    default=DEFAULT_WEBCAM_SECONDS,
                    min=MIN_WEBCAM_SECONDS,
                    max=MAX_WEBCAM_SECONDS,
                    step=STEP_WEBCAM_SECONDS,
                ),
                io.Int.Input(
                    "variation",
                    display_name="run number",
                    tooltip="Change this number to run again with unchanged inputs.",
                    default=DEFAULT_VARIATION,
                    min=MIN_VARIATION,
                    max=MAX_VARIATION,
                ),
                io.Image.Input(
                    "reference_image",
                    display_name="reference image",
                    optional=True,
                    tooltip="Optional picture of a subject to insert or replace.",
                ),
            ],
            outputs=video_outputs(),
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
                image = None if reference_image is None else await owned_io(partial(encode_png, reference_image))
                request = X2Operation(
                    X2Request(
                        prompt,
                        duration_seconds,
                        0,
                        image=image,
                        pointer_x=DEFAULT_POINTER_POSITION,
                        pointer_y=DEFAULT_POINTER_POSITION,
                    ),
                    webcam=camera,
                )
                return await generate_video(
                    request,
                    controls=build_live_options(request, webcam=camera),
                    node_id=cls.define_schema().node_id,
                )
            finally:
                await camera.close()

        return await wait_for_execution(asyncio.create_task(generate()))
