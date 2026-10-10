"""Generate a LongLive scene from an opening shot prompt and optional scheduled shots."""

from ..base import VideoNode
from comfy_api.latest import io
from ...comfy.execution import generate_video
from ...errors import ErrorCode, ConnectorError
from ...state.generation.longlive import LongLiveRequest
from ...execution.longlive.operation import LongLiveOperation
from ...execution.longlive.storyboard import parse_storyboard
from ...config.messages.inputs import LIVE_CONTROLS_STORYBOARD
from ..controls import live_control, video_outputs, generation_controls


class LongLiveGenerate(VideoNode):
    """Start a LongLive scene from its opening shot prompt, with optional later shots."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return io.Schema(
            node_id="ReactorIncLongLiveGenerate",
            display_name="LongLive: Generate Video (Reactor)",
            description="Generate a LongLive scene from an opening shot prompt, with optional scheduled shots.",
            category="Reactor/Generate",
            search_aliases=["Reactor", "LongLive", "text to video", "shots", "cuts"],
            inputs=[
                *generation_controls(),
                io.String.Input(
                    "storyboard",
                    display_name="shots (JSON)",
                    tooltip="Optionally connect Reactor LongLive: Add a Shot. [] keeps the opening shot.",
                    default="[]",
                    multiline=False,
                    advanced=True,
                ),
                live_control(),
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
        interactive: bool = False,
    ) -> io.NodeOutput:
        """Generate a LongLive video from the opening shot, scheduled shots, or live changes."""
        shots = parse_storyboard(storyboard)
        if shots and interactive:
            raise ConnectorError(ErrorCode.INVALID_INPUT, LIVE_CONTROLS_STORYBOARD)
        return await generate_video(
            LongLiveOperation(LongLiveRequest(prompt, duration_seconds, seed, shots=shots)),
            interactive=interactive,
        )
