"""Generate a LongLive video from scheduled shots and transitions."""

from typing import ClassVar
from ..base import VideoNode
from comfy_api.latest import io
from ...comfy.execution import generate_video
from ...state.generation.longlive import LongLiveRequest
from ..controls import video_outputs, generation_controls
from ...execution.longlive.operation import LongLiveOperation
from ...execution.longlive.storyboard import parse_storyboard


class LongLiveStoryboard(VideoNode):
    """Generate a video from scheduled shots and transitions."""

    contract: ClassVar[str] = "longlive-storyboard-v1"

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
                    display_name="shots (JSON)",
                    tooltip="Connect Reactor LongLive: Add a Shot, or enter a validated shot list.",
                    default="[]",
                    multiline=False,
                    advanced=True,
                ),
            ],
            outputs=video_outputs(),
        )

    @classmethod
    async def generate(
        cls,
        *,
        prompt: str,
        duration_seconds: float,
        seed: int,
        storyboard: str,
    ) -> io.NodeOutput:
        """Run the scheduled LongLive shots and record their transitions."""
        shots = parse_storyboard(storyboard)
        return await generate_video(
            LongLiveOperation(LongLiveRequest(prompt, duration_seconds, seed, shots=shots)),
            node_id=cls.define_schema().node_id,
        )
