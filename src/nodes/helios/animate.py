"""Task-specific Helios nodes with native ComfyUI media sockets."""

import asyncio
from ...media.images import image_png
from ..schema import translate_schema
from comfy_api.latest import io, Input
from ...execution.helios.request import HeliosRequest
from ...comfy.execution import generate_video, operation_fingerprint
from ..controls import live_control, video_outputs, generation_controls


class HeliosAnimate(io.ComfyNode):
    """Animate one image with a text prompt."""

    @classmethod
    async def fingerprint_inputs(cls, **_kwargs: object) -> str:
        """Include current settings and model metadata in the ComfyUI cache key."""
        return await operation_fingerprint("helios-video-v2")

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return translate_schema(
            io.Schema(
                node_id="ReactorIncHeliosAnimate",
                inputs=[
                    io.Image.Input(
                        "image",
                    ),
                    *generation_controls(),
                    live_control(),
                ],
                outputs=video_outputs(),
            )
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
        encoded = await asyncio.to_thread(image_png, image)
        return await generate_video(
            HeliosRequest(prompt, duration_seconds, seed, image=encoded),
            interactive=interactive,
            node_id=cls.define_schema().node_id,
        )
