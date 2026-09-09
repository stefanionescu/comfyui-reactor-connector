"""Continue a scene across several clips without queuing another ComfyUI run."""

import asyncio
from functools import partial
from ...media.output import owned_io
from ...media.images import image_png
from ..schema import translate_schema
from comfy_api.latest import io, Input
from ..controls import generation_controls
from ...execution.fast.continuation import FastContinueRequest
from ...comfy.execution import execute_video, wait_for_execution, operation_fingerprint
from ....config.generation.fast import (
    DEFAULT_ASPECT,
    MAX_CLIP_COUNT,
    MIN_CLIP_COUNT,
    OPTIONS_ASPECT,
    MAX_CLIP_SECONDS,
    MIN_CLIP_SECONDS,
    STEP_CLIP_SECONDS,
    DEFAULT_CLIP_COUNT,
    DEFAULT_CLIP_SECONDS,
)


class FastContinue(io.ComfyNode):
    """Join a sequence of Fast H3 clips that continue from each previous final frame."""

    @classmethod
    async def fingerprint_inputs(cls, **_kwargs: object) -> str:
        """Include current settings and model metadata in the ComfyUI cache key."""
        return await operation_fingerprint("fast-continue-v1")

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Declare the saved input names, controls, and output sockets for this node."""
        controls = generation_controls("continuation")
        controls[1] = io.Float.Input(
            "clip_seconds",
            default=DEFAULT_CLIP_SECONDS,
            min=MIN_CLIP_SECONDS,
            max=MAX_CLIP_SECONDS,
            step=STEP_CLIP_SECONDS,
        )
        return translate_schema(
            io.Schema(
                node_id="ReactorIncFastContinue",
                inputs=[
                    *controls,
                    io.Combo.Input(
                        "aspect",
                        options=OPTIONS_ASPECT,
                        default=DEFAULT_ASPECT,
                    ),
                    io.Int.Input(
                        "clip_count",
                        default=DEFAULT_CLIP_COUNT,
                        min=MIN_CLIP_COUNT,
                        max=MAX_CLIP_COUNT,
                    ),
                    io.String.Input(
                        "later_prompts",
                        multiline=True,
                        default="",
                    ),
                    io.Image.Input(
                        "image",
                        optional=True,
                    ),
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
        clip_seconds: float,
        seed: int,
        variation: int,
        aspect: str,
        clip_count: int,
        later_prompts: str,
        image: Input.Image | None = None,
    ) -> io.NodeOutput:
        """Join a sequence of Fast H3 clips that continue from each previous final frame."""
        # ComfyUI uses variation to invalidate its cache; Reactor does not consume it.
        del variation

        async def generate() -> io.NodeOutput:
            """Prepare media inside the owned task before starting the Reactor session."""
            encoded = None if image is None else await owned_io(partial(image_png, image))
            request = FastContinueRequest(
                prompt,
                clip_seconds * clip_count,
                seed,
                image=encoded,
                aspect=aspect,
                clip_seconds=clip_seconds,
                clip_count=clip_count,
                later_prompts=tuple(later_prompts.splitlines()),
            )
            return await execute_video(request, node_id=cls.define_schema().node_id)

        return await wait_for_execution(asyncio.create_task(generate()))
