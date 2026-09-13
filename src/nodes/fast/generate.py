"""Expose a queued Fast H3 clip through native ComfyUI media sockets."""

import asyncio
from functools import partial
from ...media.output import owned_io
from ...media.images import encode_png
from comfy_api.latest import io, Input
from ..controls import generation_controls
from ...state.generation.fast import FastGenerateRequest
from ...execution.fast.generate import FastGenerateOperation
from ...comfy.execution import generate_video, wait_for_execution, operation_fingerprint
from ....config.generation.fast import (
    DEFAULT_ASPECT,
    OPTIONS_ASPECT,
    MAX_CLIP_SECONDS,
    MIN_CLIP_SECONDS,
    STEP_CLIP_SECONDS,
    DEFAULT_CLIP_SECONDS,
)


class FastGenerate(io.ComfyNode):
    """Generate one clip, wait for readiness, and save its playback with sound."""

    @classmethod
    async def fingerprint_inputs(cls, **_kwargs: object) -> str:
        """Include the operation revision and private configuration token in the cache key."""
        return await operation_fingerprint("fast-queued-recording-v1")

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        duration = io.Float.Input(
            "duration_seconds",
            display_name="video duration (seconds)",
            tooltip=(
                "Fast H3 chooses a supported clip length near this value. "
                "The clip must fit the video duration limit in Reactor settings."
            ),
            default=DEFAULT_CLIP_SECONDS,
            min=MIN_CLIP_SECONDS,
            max=MAX_CLIP_SECONDS,
            step=STEP_CLIP_SECONDS,
        )
        return io.Schema(
            node_id="ReactorIncFastGenerate",
            display_name="Fast H3: Generate Video (Reactor)",
            category="Reactor/Generate",
            description="Generate a video clip with sound and optional first and last images.",
            search_aliases=["Reactor", "Fast H3", "FastH3", "audio"],
            inputs=[
                *generation_controls("fast", duration=duration),
                io.Combo.Input("aspect", display_name="aspect ratio", options=OPTIONS_ASPECT, default=DEFAULT_ASPECT),
                io.Image.Input(
                    "image",
                    display_name="starting image",
                    optional=True,
                    tooltip="Optional first frame. Connect Load Image.",
                ),
                io.Image.Input(
                    "ending_image",
                    display_name="final image",
                    optional=True,
                    tooltip="Optional last frame. Can be used with or without a first frame.",
                ),
            ],
            outputs=[
                io.Video.Output(display_name="video"),
                io.Audio.Output(display_name="audio"),
                io.String.Output(display_name="recording details"),
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
        aspect: str,
        image: Input.Image | None = None,
        ending_image: Input.Image | None = None,
    ) -> io.NodeOutput:
        """Generate a Fast H3 video with optional starting and ending images."""
        # ComfyUI uses variation to invalidate its cache; Reactor does not consume it.
        del variation

        async def generate() -> io.NodeOutput:
            """Prepare media inside the owned task before starting the Reactor session."""
            first = await owned_io(partial(encode_png, image)) if image is not None else None
            last = await owned_io(partial(encode_png, ending_image)) if ending_image is not None else None
            request = FastGenerateRequest(prompt, duration_seconds, seed, image=first, aspect=aspect, ending_image=last)
            return await generate_video(FastGenerateOperation(request), node_id=cls.define_schema().node_id)

        return await wait_for_execution(asyncio.create_task(generate()))
