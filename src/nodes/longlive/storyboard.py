"""Build and execute LongLive shots without making users write model commands."""

from comfy_api.latest import io
from ...state.generation.longlive import LongLiveRequest
from ..controls import video_outputs, generation_controls
from ...execution.longlive.request import LongLiveOperation
from ...execution.longlive.storyboard import parse_storyboard
from ...comfy.execution import generate_video, operation_fingerprint


class LongLiveStoryboard(io.ComfyNode):
    """Generate a video from scheduled shots and transitions."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return io.Schema(
            node_id="ReactorIncLongLiveStoryboard",
            display_name="LongLive: Generate Video from a Storyboard (Reactor)",
            description="Generate an opening shot and schedule later shots by chunk number.",
            category="Reactor/Generate",
            search_aliases=["Reactor", "LongLive", "shots", "cuts"],
            inputs=[
                *generation_controls(),
                io.String.Input(
                    "storyboard",
                    display_name="Shots (JSON)",
                    tooltip="Connect Reactor LongLive: Add a Shot, or enter a validated shot list.",
                    default="[]",
                    multiline=False,
                    advanced=True,
                ),
            ],
            outputs=video_outputs(),
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
        return await generate_video(
            LongLiveOperation(LongLiveRequest(prompt, duration_seconds, seed, shots=shots)),
            node_id=cls.define_schema().node_id,
        )
