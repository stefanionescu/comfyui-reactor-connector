"""Build a Helios prompt sequence using ordinary ComfyUI connections."""

import asyncio
from ...media.images import image_png
from ..schema import translate_schema
from comfy_api.latest import io, Input
from ...execution.helios.request import HeliosRequest
from ...execution.helios.prompts import parse_sequence
from ..controls import video_outputs, generation_controls
from ...comfy.execution import execute_video, operation_fingerprint


class HeliosSequence(io.ComfyNode):
    """Generate a video with prompt changes prepared before the run."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return translate_schema(
            io.Schema(
                node_id="ReactorIncHeliosSequence",
                inputs=[
                    *generation_controls(),
                    io.String.Input(
                        "sequence",
                        default="[]",
                        multiline=False,
                        advanced=True,
                    ),
                    io.Image.Input(
                        "image",
                        optional=True,
                    ),
                ],
                outputs=video_outputs(),
            )
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
