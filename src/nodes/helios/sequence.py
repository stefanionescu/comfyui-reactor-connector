"""Generate a Helios video from connected, scheduled prompts."""

import asyncio
from typing import ClassVar
from ..base import VideoNode
from ...media.images import encode_png
from comfy_api.latest import io, Input
from ...comfy.execution import generate_video
from ...state.generation.helios import HeliosRequest
from ...execution.helios.prompts import parse_sequence
from ...execution.helios.operation import HeliosOperation
from ..controls import video_outputs, generation_controls


class HeliosSequence(VideoNode):
    """Generate a video with prompt changes prepared before the run."""

    contract: ClassVar[str] = "helios-sequence-v1"

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return io.Schema(
            node_id="ReactorIncHeliosSequence",
            display_name="Helios: Generate Video from a Prompt Sequence (Reactor)",
            description="Generate a Helios video with later prompts scheduled by chunk number.",
            category="Reactor/Generate",
            search_aliases=["Reactor", "Helios", "schedule", "prompt sequence"],
            inputs=[
                *generation_controls(),
                io.String.Input(
                    "sequence",
                    display_name="prompt sequence (JSON)",
                    tooltip="Connect Reactor Helios: Add a Prompt. [] keeps the opening prompt.",
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
    ) -> io.NodeOutput:
        """Run the Helios prompt sequence and return the recorded video."""
        prompts = parse_sequence(sequence)
        encoded = await asyncio.to_thread(encode_png, image) if image is not None else None
        return await generate_video(
            HeliosOperation(HeliosRequest(prompt, duration_seconds, seed, image=encoded, prompts=prompts)),
            node_id=cls.define_schema().node_id,
        )
