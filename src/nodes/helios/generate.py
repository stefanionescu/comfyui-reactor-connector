"""Task-specific Helios nodes with native ComfyUI media sockets."""

from comfy_api.latest import io
from ..schema import translate_schema
from ...execution.helios.request import HeliosRequest
from ...comfy.execution import execute_video, operation_fingerprint
from ..controls import live_control, video_outputs, generation_controls


class HeliosGenerate(io.ComfyNode):
    """Generate a video from a text prompt."""

    @classmethod
    async def fingerprint_inputs(cls, **_kwargs: object) -> str:
        """Include current settings and model metadata in the ComfyUI cache key."""
        return await operation_fingerprint("helios-bounded-v1")

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Declare the saved input names, controls, and output sockets for this node."""
        return translate_schema(
            io.Schema(
                node_id="ReactorIncHeliosGenerate",
                inputs=[*generation_controls(), live_control()],
                outputs=video_outputs(),
            )
        )

    @classmethod
    async def execute(  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        cls,
        *,
        prompt: str,
        duration_seconds: float,
        seed: int,
        variation: int,
        interactive: bool = False,
    ) -> io.NodeOutput:
        """Generate a Helios video from the opening prompt and optional live changes."""
        # ComfyUI uses variation to invalidate its cache; Reactor does not consume it.
        del variation
        return await execute_video(
            HeliosRequest(prompt, duration_seconds, seed),
            interactive=interactive,
            node_id=cls.define_schema().node_id,
        )
