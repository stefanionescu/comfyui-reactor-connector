"""Generate a Helios video from a prompt, an optional starting image, and optional scheduled prompts."""

import asyncio
from ..base import VideoNode
from ...media.images import encode_png
from comfy_api.latest import io, Input
from ...comfy.execution import generate_video
from ...errors import ErrorCode, ConnectorError
from ...state.generation.helios import HeliosRequest
from ...execution.helios.prompts import parse_sequence
from ...execution.helios.operation import HeliosOperation
from ...config.messages.inputs import LIVE_CONTROLS_SEQUENCE
from ..controls import live_control, video_outputs, generation_controls


class HeliosGenerate(VideoNode):
    """Generate a video from a prompt, with an optional starting image and prompt sequence."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return io.Schema(
            node_id="ReactorIncHeliosGenerate",
            display_name="Helios: Generate Video (Reactor)",
            category="Reactor/Generate",
            description="Generate a video from a scene prompt, with an optional starting image and prompt sequence.",
            search_aliases=["Reactor", "Helios", "text to video", "image to video", "prompt sequence"],
            inputs=[
                *generation_controls(),
                io.String.Input(
                    "sequence",
                    display_name="prompt sequence (JSON)",
                    tooltip="Optionally connect Reactor Helios: Add a Prompt. [] keeps the opening prompt.",
                    default="[]",
                    multiline=False,
                    advanced=True,
                ),
                io.Image.Input(
                    "image",
                    display_name="starting image",
                    tooltip="Optionally connect one starting RGB image.",
                    optional=True,
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
        sequence: str,
        image: Input.Image | None = None,
        interactive: bool = False,
    ) -> io.NodeOutput:
        """Generate a Helios video from the opening prompt, scheduled prompts, or live changes."""
        prompts = parse_sequence(sequence)
        if prompts and interactive:
            raise ConnectorError(ErrorCode.INVALID_INPUT, LIVE_CONTROLS_SEQUENCE)
        encoded = await asyncio.to_thread(encode_png, image) if image is not None else None
        return await generate_video(
            HeliosOperation(HeliosRequest(prompt, duration_seconds, seed, image=encoded, prompts=prompts)),
            interactive=interactive,
        )
