"""Build a Helios prompt sequence using ordinary ComfyUI connections."""

import asyncio
from ...media.images import image_png
from comfy_api.latest import io, Input
from ...execution.helios import HeliosRequest
from ...execution.prompts import parse_sequence
from ..host import execute_video, operation_fingerprint
from ..controls import video_outputs, generation_controls


class HeliosSequence(io.ComfyNode):
    """Generate a video with prompt changes prepared before the run."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Declare the saved input names, controls, and output sockets for this node."""
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
    async def fingerprint_inputs(cls, **_kwargs: object) -> str:
        """Include current settings and model metadata in the ComfyUI cache key."""
        return await operation_fingerprint("helios-sequence-v1")

    @classmethod
    async def execute(  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.  # noqa: PLR0913 -- reason: ComfyUI requires one named argument for each saved node input.
        cls,
        *,
        prompt: str,
        duration_seconds: float,
        seed: int,
        variation: int,
        sequence: str,
        image: Input.Image | None = None,
    ) -> io.NodeOutput:
        """Run the Helios prompt sequence and return the recorded video."""
        # ComfyUI uses variation to invalidate its cache; Reactor does not consume it.
        del variation
        prompts = parse_sequence(sequence)
        encoded = await asyncio.to_thread(image_png, image) if image is not None else None
        return await execute_video(
            HeliosRequest(prompt, duration_seconds, seed, image=encoded, prompts=prompts),
            node_id=cls.define_schema().node_id,
        )
