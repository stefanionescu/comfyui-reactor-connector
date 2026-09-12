"""Record a LingBot World 2 scene with separate forward and sideways controls."""

import asyncio
from .schema import lingbot_schema
from ...media.images import encode_png
from comfy_api.latest import io, Input
from ...state.generation.lingbot import LingBotWorldRequest
from ...execution.lingbot.request import LingBotWorldOperation
from ...comfy.execution import generate_video, operation_fingerprint


class LingBotWorldExplore(io.ComfyNode):
    """Record World 2 with separate forward/back and sideways controls."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return lingbot_schema(world2=True)

    @classmethod
    async def fingerprint_inputs(cls, **_kwargs: object) -> str:
        """Include current settings and model metadata in the ComfyUI cache key."""
        return await operation_fingerprint("lingbot-world-2-video-v2")

    @classmethod
    async def execute(  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.  # noqa: PLR0913 -- reason: ComfyUI requires one named argument for each saved node input.
        cls,
        *,
        image: Input.Image,
        prompt: str,
        duration_seconds: float,
        seed: int,
        variation: int,
        movement: str,
        lateral: str,
        look_horizontal: str,
        look_vertical: str,
        rotation_speed_deg: float,
        interactive: bool = False,
    ) -> io.NodeOutput:
        """Explore the starting image with LingBot World 2 movement and camera controls."""
        # ComfyUI uses variation to invalidate its cache; Reactor does not consume it.
        del variation
        encoded = await asyncio.to_thread(encode_png, image)
        request = LingBotWorldRequest(
            prompt,
            duration_seconds,
            seed,
            encoded,
            movement="idle" if interactive else movement,
            look_horizontal="idle" if interactive else look_horizontal,
            look_vertical="idle" if interactive else look_vertical,
            rotation_speed_deg=rotation_speed_deg,
            lateral="idle" if interactive else lateral,
        )
        return await generate_video(
            LingBotWorldOperation(request),
            interactive=interactive,
            node_id=cls.define_schema().node_id,
        )
