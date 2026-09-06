"""Task-specific Helios nodes with native ComfyUI media sockets."""

import asyncio

from comfy_api.latest import Input, io

from ..execution.session import HeliosRequest
from ..media.images import image_png
from .controls import generation_controls, live_control, video_outputs
from .host import execute_helios, helios_fingerprint


class HeliosGenerate(io.ComfyNode):
    """Generate a video from a text prompt."""

    @classmethod
    async def fingerprint_inputs(cls, **kwargs: object) -> str:
        return await helios_fingerprint()

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="ReactorIncHeliosGenerate",
            display_name="Reactor Helios: Generate video",
            category="Reactor/Generate",
            inputs=[*generation_controls(), live_control()],
            outputs=video_outputs(),
            description="Generate a video with your Reactor account. Help includes usage limits.",
            search_aliases=["Reactor", "Helios", "text to video"],
        )

    @classmethod
    async def execute(
        cls,
        prompt: str,
        duration_seconds: float,
        seed: int,
        variation: int,
        interactive: bool = False,
    ) -> io.NodeOutput:
        return await execute_helios(
            HeliosRequest(prompt, duration_seconds, seed),
            interactive=interactive,
            node_id=cls.define_schema().node_id,
        )


class HeliosAnimate(io.ComfyNode):
    """Animate one image with a text prompt."""

    @classmethod
    async def fingerprint_inputs(cls, **kwargs: object) -> str:
        return await helios_fingerprint()

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="ReactorIncHeliosAnimate",
            display_name="Reactor Helios: Animate an image",
            category="Reactor/Generate",
            inputs=[
                io.Image.Input(
                    "image", display_name="Starting image", tooltip="Connect one RGB image."
                ),
                *generation_controls(),
                live_control(),
            ],
            outputs=video_outputs(),
            search_aliases=["Reactor", "Helios", "image to video"],
            description="Animate one image through Reactor. Prompt and image are applied together.",
        )

    @classmethod
    async def execute(
        cls,
        image: Input.Image,
        prompt: str,
        duration_seconds: float,
        seed: int,
        variation: int,
        interactive: bool = False,
    ) -> io.NodeOutput:
        encoded = await asyncio.to_thread(image_png, image)
        return await execute_helios(
            HeliosRequest(prompt, duration_seconds, seed, image=encoded),
            interactive=interactive,
            node_id=cls.define_schema().node_id,
        )
