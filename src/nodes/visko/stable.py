"""Generate Visko Stable video with synchronized audio."""

import asyncio
from typing import ClassVar
from ...media.output import owned_io
from ..schema import translate_schema
from ...media.images import encode_png
from comfy_api.latest import io, Input
from ..controls import live_control, generation_controls
from ...execution.visko.request import ViskoStableRequest
from ...comfy.execution import generate_video, wait_for_execution, operation_fingerprint


class ViskoStableGenerate(io.ComfyNode):
    """Generate video and sound from a prompt and an optional starting image."""

    node_id: ClassVar[str] = "ReactorIncViskoStableGenerate"
    request_type: ClassVar[type[ViskoStableRequest]] = ViskoStableRequest

    @classmethod
    async def fingerprint_inputs(cls, **_kwargs: object) -> str:
        """Include current settings and model metadata in the ComfyUI cache key."""
        return await operation_fingerprint(f"{cls.node_id}-recording-v1")

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return translate_schema(
            io.Schema(
                node_id=cls.node_id,
                inputs=[
                    *generation_controls("visko"),
                    io.String.Input(
                        "audio_prompt",
                        default="",
                        multiline=True,
                    ),
                    io.String.Input(
                        "resolution",
                        default="",
                    ),
                    io.Boolean.Input(
                        "audio_enabled",
                        default=True,
                    ),
                    io.Boolean.Input(
                        "prompt_passthrough",
                        default=False,
                    ),
                    io.Image.Input(
                        "image",
                        optional=True,
                    ),
                    live_control(),
                ],
                outputs=[
                    io.Video.Output(),
                    io.Audio.Output(),
                    io.String.Output(),
                ],
            )
        )

    @classmethod
    async def execute(  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.  # noqa: PLR0913 -- reason: ComfyUI requires one named argument for each saved node input.
        cls,
        *,
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
        """Generate Visko video and audio from the selected text, image, and sound controls."""
        # ComfyUI uses variation to invalidate its cache; Reactor does not consume it.
        del variation

        async def generate() -> io.NodeOutput:
            """Prepare media inside the owned task before starting the Reactor session."""
            source_image = image
            encoded = None if source_image is None else await owned_io(lambda: encode_png(source_image))
            return await generate_video(
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
