"""Animate an input image with Helios."""

import asyncio
from ...media.images import encode_png
from comfy_api.latest import io, Input
from ...state.generation.helios import HeliosRequest
from ...execution.helios.operation import HeliosOperation
from ...comfy.execution import generate_video, operation_fingerprint
from ..controls import live_control, video_outputs, generation_controls


class HeliosAnimate(io.ComfyNode):
    """Animate one image with a text prompt."""

    @classmethod
    async def fingerprint_inputs(cls, **_kwargs: object) -> str:
        """Include the operation revision and private configuration token in the cache key."""
        return await operation_fingerprint("helios-video-v2")

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return io.Schema(
            node_id="ReactorIncHeliosAnimate",
            display_name="Helios: Animate an Image (Reactor)",
            category="Reactor/Generate",
            description="Animate one image through Reactor. Prompt and image are applied together.",
            search_aliases=["Reactor", "Helios", "image to video"],
            inputs=[
                io.Image.Input("image", display_name="starting image", tooltip="Connect one RGB image."),
                *generation_controls(),
                live_control(),
            ],
            outputs=video_outputs(),
        )

    @classmethod
    async def execute(  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.  # noqa: PLR0913 -- reason: ComfyUI requires one named argument for each saved node input.
        cls,
        *,
        image: Input.Image,
        prompt: str,
        duration_seconds: float,
        seed: int,
        variation: int,
        interactive: bool = False,
    ) -> io.NodeOutput:
        """Animate the starting image with Helios and optional live changes."""
        # ComfyUI uses variation to invalidate its cache; Reactor does not consume it.
        del variation
        encoded = await asyncio.to_thread(encode_png, image)
        return await generate_video(
            HeliosOperation(HeliosRequest(prompt, duration_seconds, seed, image=encoded)),
            interactive=interactive,
            node_id=cls.define_schema().node_id,
        )
