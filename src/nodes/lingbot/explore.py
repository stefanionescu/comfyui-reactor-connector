"""Record a LingBot scene from an image and camera directions."""

import asyncio
from .schema import lingbot_schema
from ...media.images import encode_png
from comfy_api.latest import io, Input
from ...state.generation.lingbot import LingBotRequest
from ...execution.lingbot.operation import LingBotOperation
from ...comfy.execution import generate_video, operation_fingerprint


class LingBotExplore(io.ComfyNode):
    """Record a LingBot scene using a starting image and camera directions."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return lingbot_schema(world2=False)

    @classmethod
    async def fingerprint_inputs(cls, **_kwargs: object) -> str:
        """Include the operation revision and private configuration token in the cache key."""
        return await operation_fingerprint("lingbot-video-v2")

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
        look_horizontal: str,
        look_vertical: str,
        rotation_speed_deg: float,
        interactive: bool = False,
    ) -> io.NodeOutput:
        """Explore the starting image with the selected LingBot camera controls."""
        # ComfyUI uses variation to invalidate its cache; Reactor does not consume it.
        del variation
        encoded = await asyncio.to_thread(encode_png, image)
        request = LingBotRequest(
            prompt=prompt,
            duration_seconds=duration_seconds,
            seed=seed,
            image=encoded,
            movement="idle" if interactive else movement,
            look_horizontal="idle" if interactive else look_horizontal,
            look_vertical="idle" if interactive else look_vertical,
            rotation_speed_deg=rotation_speed_deg,
        )
        return await generate_video(
            LingBotOperation(request),
            interactive=interactive,
            node_id=cls.define_schema().node_id,
        )
