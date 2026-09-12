"""Generate a video from a text prompt with Helios."""

from comfy_api.latest import io
from ...state.generation.helios import HeliosRequest
from ...execution.helios.operation import HeliosOperation
from ...comfy.execution import generate_video, operation_fingerprint
from ..controls import live_control, video_outputs, generation_controls


class HeliosGenerate(io.ComfyNode):
    """Generate a video from a text prompt."""

    @classmethod
    async def fingerprint_inputs(cls, **_kwargs: object) -> str:
        """Include the operation revision and private configuration token in the cache key."""
        return await operation_fingerprint("helios-video-v2")

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return io.Schema(
            node_id="ReactorIncHeliosGenerate",
            display_name="Helios: Generate Video (Reactor)",
            category="Reactor/Generate",
            description="Generate a video from a scene prompt using your Reactor account.",
            search_aliases=["Reactor", "Helios", "text to video"],
            inputs=[*generation_controls(), live_control()],
            outputs=video_outputs(),
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
        return await generate_video(
            HeliosOperation(HeliosRequest(prompt, duration_seconds, seed)),
            interactive=interactive,
            node_id=cls.define_schema().node_id,
        )
