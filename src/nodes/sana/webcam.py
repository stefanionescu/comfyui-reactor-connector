"""Record edits from a camera explicitly enabled in the owning browser."""

from comfy_api.latest import io
from ...media.webcam import WebcamFrames
from ...state.generation.sana import SanaRequest
from ...comfy.interaction import build_live_options
from ...execution.sana.operation import SanaOperation
from ..controls import video_outputs, generation_controls
from ...comfy.execution import generate_video, operation_fingerprint
from ....config.generation.video import MAX_ANCHOR_INTERVAL, MIN_ANCHOR_INTERVAL, DEFAULT_ANCHOR_INTERVAL


class SanaWebcam(io.ComfyNode):
    """Open the webcam controls and record the SANA video edit."""

    @classmethod
    async def fingerprint_inputs(cls, **_kwargs: object) -> str:
        """Include the operation revision and private configuration token in the cache key."""
        return await operation_fingerprint("sana-webcam-v1")

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return io.Schema(
            node_id="ReactorIncSanaWebcam",
            display_name="SANA: Edit a Webcam (Reactor)",
            description="Enable a webcam in the live panel, then record an edited video.",
            category="Reactor/Live",
            search_aliases=[],
            inputs=[
                *generation_controls("webcam"),
                io.Int.Input(
                    "anchor_interval",
                    display_name="Source refresh interval (chunks)",
                    tooltip="Return to the camera source after this many model chunks. Use 0 to turn this off.",
                    default=DEFAULT_ANCHOR_INTERVAL,
                    min=MIN_ANCHOR_INTERVAL,
                    max=MAX_ANCHOR_INTERVAL,
                ),
            ],
            outputs=video_outputs(),
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
            request = SanaOperation(
                SanaRequest(prompt, duration_seconds, seed, anchor_interval=anchor_interval), webcam=camera
            )
            return await generate_video(
                request,
                controls=build_live_options(request, webcam=camera),
                node_id=cls.define_schema().node_id,
            )
        finally:
            await camera.close()
