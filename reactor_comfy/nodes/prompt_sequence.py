"""Build a Helios prompt sequence using ordinary ComfyUI connections."""

import asyncio

from comfy_api.latest import Input, io

from ..execution.helios import HeliosRequest
from ..execution.prompt_sequence import ScheduledPrompt, append_prompt, parse_sequence
from ..media.images import image_png
from .controls import generation_controls, video_outputs
from .host import execute_helios, operation_fingerprint


class HeliosAddPrompt(io.ComfyNode):
    """Add one later prompt without opening a Reactor session."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="ReactorIncHeliosAddPrompt",
            display_name="Reactor Helios: Add a prompt",
            category="Reactor/Plans",
            inputs=[
                io.String.Input(
                    "previous",
                    display_name="Previous steps (JSON)",
                    default="[]",
                    multiline=False,
                    advanced=True,
                    tooltip="Leave [] for the first later prompt, or connect the previous builder.",
                ),
                io.Int.Input(
                    "chunk",
                    display_name="Start chunk",
                    default=1,
                    min=1,
                    max=100_000,
                    tooltip="When this prompt starts. A Helios chunk contains 33 frames.",
                ),
                io.String.Input(
                    "prompt",
                    display_name="Scene prompt",
                    placeholder="Scene prompt",
                    default="Sunlight reaches the forest floor as the camera moves forward.",
                    multiline=True,
                    tooltip="Describe the scene and motion after this change.",
                ),
            ],
            outputs=[io.String.Output(display_name="sequence")],
            description="Add a later Helios prompt. Preparing the sequence uses no credits.",
            search_aliases=["Reactor", "Helios", "schedule", "prompt"],
        )

    @classmethod
    def execute(cls, previous: str, chunk: int, prompt: str) -> io.NodeOutput:
        return io.NodeOutput(append_prompt(previous, ScheduledPrompt(chunk, prompt)))


class HeliosSequence(io.ComfyNode):
    """Generate a video with prompt changes prepared before the run."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="ReactorIncHeliosSequence",
            display_name="Reactor Helios: Generate a prompt sequence",
            category="Reactor/Generate",
            inputs=[
                *generation_controls(),
                io.String.Input(
                    "sequence",
                    display_name="Prompt sequence (JSON)",
                    default="[]",
                    multiline=False,
                    advanced=True,
                    tooltip="Connect Reactor Helios: Add a prompt. [] keeps the opening prompt.",
                ),
                io.Image.Input(
                    "image",
                    display_name="Starting image",
                    optional=True,
                    tooltip="Optionally connect one starting RGB image.",
                ),
            ],
            outputs=video_outputs(),
            description="Generate a Helios video with later prompts scheduled by chunk number.",
            search_aliases=["Reactor", "Helios", "schedule", "prompt sequence"],
        )

    @classmethod
    async def fingerprint_inputs(cls, **kwargs: object) -> str:
        return await operation_fingerprint("helios-sequence-v1")

    @classmethod
    async def execute(
        cls,
        prompt: str,
        duration_seconds: float,
        seed: int,
        variation: int,
        sequence: str,
        image: Input.Image | None = None,
    ) -> io.NodeOutput:
        prompts = parse_sequence(sequence)
        encoded = await asyncio.to_thread(image_png, image) if image is not None else None
        return await execute_helios(
            HeliosRequest(prompt, duration_seconds, seed, image=encoded, prompts=prompts),
            node_id=cls.define_schema().node_id,
        )
