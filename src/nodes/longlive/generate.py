"""Build and execute LongLive shots without making users write model commands."""

from comfy_api.latest import io
from ...execution.storyboard import LongLiveRequest
from ..host import execute_video, operation_fingerprint
from ..controls import live_control, video_outputs, generation_controls


class LongLiveGenerate(io.ComfyNode):
    """Start a LongLive scene from its opening shot prompt."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Declare the saved input names, controls, and output sockets for this node."""
        return io.Schema(
            node_id="ReactorIncLongLiveGenerate",
            display_name="Reactor LongLive: Generate video",
            category="Reactor/Generate",
            inputs=[*generation_controls(), live_control()],
            outputs=video_outputs(),
            description="Generate a short LongLive scene from an opening shot prompt.",
            search_aliases=["Reactor", "LongLive", "text to video"],
        )

    @classmethod
    async def fingerprint_inputs(cls, **_kwargs: object) -> str:
        """Include current settings and model metadata in the ComfyUI cache key."""
        return await operation_fingerprint("longlive-bounded-v1")

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
        """Generate a LongLive video with optional live prompt changes."""
        # ComfyUI uses variation to invalidate its cache; Reactor does not consume it.
        del variation
        return await execute_video(
            LongLiveRequest(prompt, duration_seconds, seed),
            interactive=interactive,
            node_id=cls.define_schema().node_id,
        )
