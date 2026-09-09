"""Record edits from a camera explicitly enabled in the owning browser."""

from comfy_api.latest import io
from ...live.state import LiveOptions
from ..schema import translate_schema
from ...media.webcam import WebcamFrames
from ...execution.sana.request import SanaRequest
from ..controls import video_outputs, generation_controls
from ....config.generation.video import MAX_ANCHOR_INTERVAL
from ...comfy.execution import execute_video, operation_fingerprint


class SanaWebcam(io.ComfyNode):
    """Open the webcam controls and record the SANA video edit."""

    @classmethod
    async def fingerprint_inputs(cls, **_kwargs: object) -> str:
        """Include current settings and model metadata in the ComfyUI cache key."""
        return await operation_fingerprint("sana-webcam-v1")

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Declare the saved input names, controls, and output sockets for this node."""
        return translate_schema(
            io.Schema(
                node_id="ReactorIncSanaWebcam",
                inputs=[
                    *generation_controls("webcam"),
                    io.Int.Input(
                        "anchor_interval",
                        default=0,
                        min=0,
                        max=MAX_ANCHOR_INTERVAL,
                    ),
                ],
                outputs=video_outputs(),
            )
        )

    @classmethod
    async def execute(  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        cls, *, prompt: str, duration_seconds: float, seed: int, variation: int, anchor_interval: int
    ) -> io.NodeOutput:
        """Open the webcam controls and record the SANA video edit."""
        # ComfyUI uses variation to invalidate its cache; Reactor does not consume it.
        del variation
        camera = WebcamFrames()
        try:
            request = SanaRequest(prompt, duration_seconds, seed, webcam=camera, anchor_interval=anchor_interval)
            return await execute_video(
                request,
                controls=LiveOptions(request.model_name, prompt, camera),
                node_id=cls.define_schema().node_id,
            )
        finally:
            await camera.close()
