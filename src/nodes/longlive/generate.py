"""Generate a LongLive scene from an opening shot prompt."""

from typing import ClassVar
from ..base import VideoNode
from comfy_api.latest import io
from ...comfy.execution import generate_video
from ...state.generation.longlive import LongLiveRequest
from ...execution.longlive.operation import LongLiveOperation
from ..controls import live_control, video_outputs, generation_controls


class LongLiveGenerate(VideoNode):
    """Start a LongLive scene from its opening shot prompt."""

    contract: ClassVar[str] = "longlive-video-v2"

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return io.Schema(
            node_id="ReactorIncLongLiveGenerate",
            display_name="LongLive: Generate Video (Reactor)",
            description="Generate a short LongLive scene from an opening shot prompt.",
            category="Reactor/Generate",
            search_aliases=["Reactor", "LongLive", "text to video"],
            inputs=[*generation_controls(), live_control()],
            outputs=video_outputs(),
        )

    @classmethod
    async def generate(
        cls,
        *,
        prompt: str,
        duration_seconds: float,
        seed: int,
        interactive: bool = False,
    ) -> io.NodeOutput:
        """Generate a LongLive video with optional live prompt changes."""
        return await generate_video(
            LongLiveOperation(LongLiveRequest(prompt, duration_seconds, seed)),
            interactive=interactive,
            node_id=cls.define_schema().node_id,
        )
