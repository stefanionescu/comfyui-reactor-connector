"""Build and execute LongLive shots without making users write model commands."""

from comfy_api.latest import io
from ..host import execute_video, operation_fingerprint
from ..controls import video_outputs, generation_controls
from ...execution.storyboard import LongLiveRequest, parse_storyboard


class LongLiveStoryboard(io.ComfyNode):
    """Prepare scheduled soft shots and hard cuts before generation starts."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Declare the saved input names, controls, and output sockets for this node."""
        return io.Schema(
            node_id="ReactorIncLongLiveStoryboard",
            display_name="Reactor LongLive: Create a storyboard",
            category="Reactor/Generate",
            inputs=[
                *generation_controls(),
                io.String.Input(
                    "storyboard",
                    display_name="Shots (JSON)",
                    default="[]",
                    multiline=False,
                    advanced=True,
                    tooltip="Connect Reactor LongLive: Add a shot, or enter a validated shot list.",
                ),
            ],
            outputs=video_outputs(),
            description="Generate an opening shot and schedule later shots by chunk number.",
            search_aliases=["Reactor", "LongLive", "shots", "cuts"],
        )

    @classmethod
    async def fingerprint_inputs(cls, **_kwargs: object) -> str:
        """Include current settings and model metadata in the ComfyUI cache key."""
        return await operation_fingerprint("longlive-storyboard-v1")

    @classmethod
    async def execute(  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        cls,
        *,
        prompt: str,
        duration_seconds: float,
        seed: int,
        variation: int,
        storyboard: str,
    ) -> io.NodeOutput:
        """Run the scheduled LongLive shots and record their transitions."""
        # ComfyUI uses variation to invalidate its cache; Reactor does not consume it.
        del variation
        shots = parse_storyboard(storyboard)
        return await execute_video(
            LongLiveRequest(prompt, duration_seconds, seed, shots=shots),
            node_id=cls.define_schema().node_id,
        )
