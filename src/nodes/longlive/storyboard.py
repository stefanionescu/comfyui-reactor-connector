"""Build and execute LongLive shots without making users write model commands."""

from comfy_api.latest import io
from ..schema import translate_schema
from ...execution.longlive.request import LongLiveRequest
from ..controls import video_outputs, generation_controls
from ...execution.longlive.storyboard import parse_storyboard
from ...comfy.execution import execute_video, operation_fingerprint


class LongLiveStoryboard(io.ComfyNode):
    """Prepare scheduled soft shots and hard cuts before generation starts."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return translate_schema(
            io.Schema(
                node_id="ReactorIncLongLiveStoryboard",
                inputs=[
                    *generation_controls(),
                    io.String.Input(
                        "storyboard",
                        default="[]",
                        multiline=False,
                        advanced=True,
                    ),
                ],
                outputs=video_outputs(),
            )
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
