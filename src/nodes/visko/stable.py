"""Generate Visko Stable video with synchronized audio."""

import asyncio
from typing import ClassVar
from ...media.output import owned_io
from ...media.images import encode_png
from comfy_api.latest import io, Input
from ...state.generation.visko import ViskoStableRequest
from ..controls import live_control, generation_controls
from ...execution.visko.request import ViskoStableOperation
from ...comfy.execution import generate_video, wait_for_execution, operation_fingerprint


class ViskoStableGenerate(io.ComfyNode):
    """Generate video and sound from a prompt and an optional starting image."""

    node_id: ClassVar[str] = "ReactorIncViskoStableGenerate"
    display_name: ClassVar[str] = "Visko Stable: Generate Video (Reactor)"
    request_type: ClassVar[type[ViskoStableRequest]] = ViskoStableRequest
    operation_type: ClassVar[type[ViskoStableOperation]] = ViskoStableOperation

    @classmethod
    async def fingerprint_inputs(cls, **_kwargs: object) -> str:
        """Include current settings and model metadata in the ComfyUI cache key."""
        return await operation_fingerprint(f"{cls.node_id}-recording-v1")

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return io.Schema(
            node_id=cls.node_id,
            display_name=cls.display_name,
            description="Generate video with sound from text or a starting image.",
            category="Reactor/Generate",
            search_aliases=["Reactor", "Visko", "audio", "image to video"],
            inputs=[
                *generation_controls("visko"),
                io.String.Input(
                    "audio_prompt",
                    display_name="Sound prompt",
                    placeholder="Sound prompt",
                    tooltip="Describe the sound briefly, or leave blank to use the picture.",
                    default="",
                    multiline=True,
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
                io.Video.Output(display_name="Video"),
                io.Audio.Output(display_name="Audio"),
                io.String.Output(display_name="Recording details"),
            ],
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
            request = cls.request_type(
                prompt,
                duration_seconds,
                seed,
                image=encoded,
                audio_prompt=audio_prompt,
                resolution=resolution,
                audio_enabled=audio_enabled,
                prompt_passthrough=prompt_passthrough,
            )
            return await generate_video(
                cls.operation_type(request),
                interactive=interactive,
                node_id=cls.define_schema().node_id,
            )

        return await wait_for_execution(asyncio.create_task(generate()))
