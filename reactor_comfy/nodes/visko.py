"""Expose each Visko deployment with native synchronized video and audio outputs."""

import asyncio
from typing import ClassVar

from comfy_api.latest import Input, io

from ..execution.visko import ViskoDynamicRequest, ViskoStableRequest
from ..media.file_output import owned_io
from ..media.images import image_png
from .controls import generation_controls, live_control
from .host import execute_video, operation_fingerprint, wait_for_execution


class ViskoStableGenerate(io.ComfyNode):
    """Generate video and sound from a prompt and an optional starting image."""

    node_id: ClassVar[str] = "ReactorIncViskoStableGenerate"
    display_name: ClassVar[str] = "Reactor Visko Stable: Generate video"
    request_type: ClassVar[type[ViskoStableRequest]] = ViskoStableRequest

    @classmethod
    async def fingerprint_inputs(cls, **kwargs: object) -> str:
        return await operation_fingerprint(f"{cls.node_id}-recording-v1")

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id=cls.node_id,
            display_name=cls.display_name,
            category="Reactor/Generate",
            inputs=[
                *generation_controls("A small stream flows over smooth stones in a quiet forest."),
                io.String.Input(
                    "audio_prompt",
                    display_name="Sound prompt",
                    placeholder="Sound prompt",
                    default="",
                    multiline=True,
                    tooltip="Describe the sound briefly, or leave blank to use the picture.",
                ),
                io.String.Input(
                    "resolution",
                    display_name="Resolution",
                    default="",
                    tooltip="Leave blank for the model default, or use an offered resolution name.",
                ),
                io.Boolean.Input(
                    "audio_enabled",
                    display_name="Include sound",
                    default=True,
                    tooltip="Generate sound. When false, the model's audio track is silent.",
                ),
                io.Boolean.Input(
                    "prompt_passthrough",
                    display_name="Use prompt unchanged",
                    default=False,
                    tooltip="Use your exact prompt without Reactor preparing it first.",
                ),
                io.Image.Input(
                    "image",
                    display_name="Starting image",
                    optional=True,
                    tooltip="Optional single RGB starting image.",
                ),
                live_control(),
            ],
            outputs=[
                io.Video.Output(display_name="video"),
                io.Audio.Output(display_name="audio"),
                io.String.Output(display_name="metadata"),
            ],
            description="Generate video with sound from text or a starting image.",
            search_aliases=["Reactor", "Visko", "audio", "image to video"],
        )

    @classmethod
    async def execute(
        cls,
        prompt: str,
        duration_seconds: float,
        seed: int,
        variation: int,
        audio_prompt: str,
        resolution: str,
        audio_enabled: bool,
        prompt_passthrough: bool,
        image: Input.Image | None = None,
        interactive: bool = False,
    ) -> io.NodeOutput:
        async def generate() -> io.NodeOutput:
            source_image = image
            encoded = (
                None if source_image is None else await owned_io(lambda: image_png(source_image))
            )
            return await execute_video(
                cls.request_type(
                    prompt,
                    duration_seconds,
                    seed,
                    image=encoded,
                    audio_prompt=audio_prompt,
                    resolution=resolution,
                    audio_enabled=audio_enabled,
                    prompt_passthrough=prompt_passthrough,
                ),
                interactive=interactive,
                node_id=cls.define_schema().node_id,
            )

        return await wait_for_execution(asyncio.create_task(generate()))


class ViskoDynamicGenerate(ViskoStableGenerate):
    """Use the Dynamic deployment with its own stable public node ID."""

    node_id: ClassVar[str] = "ReactorIncViskoDynamicGenerate"
    display_name: ClassVar[str] = "Reactor Visko Dynamic: Generate video"
    request_type: ClassVar[type[ViskoStableRequest]] = ViskoDynamicRequest
