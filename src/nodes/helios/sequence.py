"""Generate a Helios video from connected, scheduled prompts."""

import asyncio
from ...media.images import encode_png
from comfy_api.latest import io, Input
from ...state.generation.helios import HeliosRequest
from ...execution.helios.prompts import parse_sequence
from ...execution.helios.operation import HeliosOperation
from ..controls import video_outputs, generation_controls
from ...comfy.execution import generate_video, operation_fingerprint


class HeliosSequence(io.ComfyNode):
    """Generate a video with prompt changes prepared before the run."""

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
                    display_name="Prompt sequence (JSON)",
                    tooltip="Connect Reactor Helios: Add a Prompt. [] keeps the opening prompt.",
                    default="[]",
                    multiline=False,
                    advanced=True,
                ),
                io.Image.Input(
                    "image",
                    display_name="Starting image",
                    tooltip="Optionally connect one starting RGB image.",
                    optional=True,
                ),
            ],
            outputs=video_outputs(),
        )

    @classmethod
    async def fingerprint_inputs(cls, **_kwargs: object) -> str:
        """Include the operation revision and private configuration token in the cache key."""
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
        encoded = await asyncio.to_thread(encode_png, image) if image is not None else None
        return await generate_video(
            HeliosOperation(HeliosRequest(prompt, duration_seconds, seed, image=encoded, prompts=prompts)),
            node_id=cls.define_schema().node_id,
        )
