"""Record a LingBot scene from an image and camera directions."""

import asyncio
from typing import ClassVar
from ..base import VideoNode
from .schema import lingbot_schema
from ...media.images import encode_png
from comfy_api.latest import io, Input
from ...comfy.execution import generate_video
from ...state.generation.lingbot import LingBotRequest
from ...execution.lingbot.operation import LingBotOperation


class LingBotExplore(VideoNode):
    """Record a LingBot scene using a starting image and camera directions."""

    contract: ClassVar[str] = "lingbot-video-v2"

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return lingbot_schema(world2=False)

    @classmethod
    async def generate(  # noqa: PLR0913 -- reason: ComfyUI requires one named argument for each saved node input.
        cls,
        *,
        image: Input.Image,
        prompt: str,
        duration_seconds: float,
        seed: int,
        movement: str,
        look_horizontal: str,
        look_vertical: str,
        rotation_speed_deg: float,
        interactive: bool = False,
    ) -> io.NodeOutput:
        """Explore the starting image with the selected LingBot camera controls."""
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
