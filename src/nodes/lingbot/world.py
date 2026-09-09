"""Record a LingBot World 2 scene with separate forward and sideways controls."""

import asyncio
from .schema import lingbot_schema
from ...media.images import image_png
from comfy_api.latest import io, Input
from ...execution.lingbot.request import LingBotWorld2Request
from ...comfy.execution import execute_video, operation_fingerprint


class LingBotWorld2Explore(io.ComfyNode):
    """Record World 2 with separate forward/back and sideways controls."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Declare the saved input names, controls, and output sockets for this node."""
        return lingbot_schema(world2=True)

    @classmethod
    async def fingerprint_inputs(cls, **_kwargs: object) -> str:
        """Include current settings and model metadata in the ComfyUI cache key."""
        return await operation_fingerprint("lingbot-world-2-bounded-v1")

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
        encoded = await asyncio.to_thread(image_png, image)
        return await execute_video(
            LingBotWorld2Request(
                prompt,
                duration_seconds,
                seed,
                encoded,
                "idle" if interactive else movement,
                "idle" if interactive else look_horizontal,
                "idle" if interactive else look_vertical,
                rotation_speed_deg,
                "idle" if interactive else lateral,
            ),
            interactive=interactive,
            node_id=cls.define_schema().node_id,
        )
