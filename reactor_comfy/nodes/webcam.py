"""Record edits from a camera explicitly enabled in the owning browser."""

import asyncio
from functools import partial

from comfy_api.latest import Input, io

from ..execution.sana import SanaRequest
from ..execution.x2 import X2Request
from ..live.control_lease import LiveOptions
from ..media.file_output import owned_io
from ..media.images import image_png
from ..media.webcam import WebcamFrames
from .controls import generation_controls, video_outputs
from .host import execute_video, operation_fingerprint, wait_for_execution


class SanaWebcam(io.ComfyNode):
    @classmethod
    async def fingerprint_inputs(cls, **kwargs: object) -> str:
        return await operation_fingerprint("sana-webcam-v1")

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="ReactorIncSanaWebcam",
            display_name="Reactor SANA: Edit a webcam",
            category="Reactor/Live",
            inputs=[
                *generation_controls("Turn the scene into a watercolor painting."),
                io.Int.Input(
                    "anchor_interval",
                    display_name="Anchor interval",
                    default=0,
                    min=0,
                    max=1000,
                    tooltip=(
                        "Return to the camera source after this many model chunks. Use 0 to "
                        "turn this off."
                    ),
                ),
            ],
            outputs=video_outputs(),
            description="Enable a webcam in the live panel, then record an edited video.",
        )

    @classmethod
    async def execute(
        cls, prompt: str, duration_seconds: float, seed: int, variation: int, anchor_interval: int
    ) -> io.NodeOutput:
        camera = WebcamFrames()
        try:
            request = SanaRequest(
                prompt, duration_seconds, seed, webcam=camera, anchor_interval=anchor_interval
            )
            return await execute_video(
                request,
                controls=LiveOptions(request.model_name, prompt, camera),
                node_id=cls.define_schema().node_id,
            )
        finally:
            await camera.close()


class X2Webcam(io.ComfyNode):
    @classmethod
    async def fingerprint_inputs(cls, **kwargs: object) -> str:
        return await operation_fingerprint("x2-webcam-v1")

    @classmethod
    def define_schema(cls) -> io.Schema:
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
                    default="Turn the scene into a watercolor painting.",
                ),
                io.Float.Input(
                    "duration_seconds",
                    display_name="Video length (seconds)",
                    default=10,
                    min=0.1,
                    max=60,
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
    async def execute(
        cls,
        prompt: str,
        duration_seconds: float,
        variation: int,
        reference_image: Input.Image | None = None,
    ) -> io.NodeOutput:
        async def generate() -> io.NodeOutput:
            camera = WebcamFrames()
            try:
                image = (
                    None
                    if reference_image is None
                    else await owned_io(partial(image_png, reference_image))
                )
                request = X2Request(prompt, duration_seconds, 0, image=image, webcam=camera)
                return await execute_video(
                    request,
                    controls=LiveOptions(request.model_name, prompt, camera),
                    node_id=cls.define_schema().node_id,
                )
            finally:
                await camera.close()

        return await wait_for_execution(asyncio.create_task(generate()))
