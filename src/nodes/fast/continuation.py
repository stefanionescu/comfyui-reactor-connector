"""Continue a scene across several clips without queuing another ComfyUI run."""

import asyncio
from functools import partial
from ...media.output import owned_io
from ...media.images import image_png
from comfy_api.latest import io, Input
from ..controls import generation_controls
from ....config.prompts import FAST_CONTINUATION_PROMPT
from ...execution.fast.continuation import FastContinueRequest
from ....config.generation.fast import DEFAULT_ASPECT, OPTIONS_ASPECT
from ..host import execute_video, wait_for_execution, operation_fingerprint
from ....config.generation.fast import (
    MAX_CLIP_COUNT,
    MIN_CLIP_COUNT,
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
        controls = generation_controls(FAST_CONTINUATION_PROMPT)
        controls[1] = io.Float.Input(
            "clip_seconds",
            display_name="Clip length (seconds)",
            default=DEFAULT_CLIP_SECONDS,
            min=MIN_CLIP_SECONDS,
            max=MAX_CLIP_SECONDS,
            step=STEP_CLIP_SECONDS,
            tooltip="Length of each clip. Fast H3 chooses the closest supported length.",
        )
        return io.Schema(
            node_id="ReactorIncFastContinue",
            display_name="Reactor Fast H3: Continue a scene",
            category="Reactor/Generate",
            inputs=[
                *controls,
                io.Combo.Input(
                    "aspect",
                    display_name="Aspect ratio",
                    options=OPTIONS_ASPECT,
                    default=DEFAULT_ASPECT,
                ),
                io.Int.Input(
                    "clip_count",
                    display_name="Number of clips",
                    default=DEFAULT_CLIP_COUNT,
                    min=MIN_CLIP_COUNT,
                    max=MAX_CLIP_COUNT,
                    tooltip=(
                        "Total clips in one paid session. Their combined length must fit the video duration limit."
                    ),
                ),
                io.String.Input(
                    "later_prompts",
                    display_name="Later prompts",
                    placeholder="Later prompts",
                    multiline=True,
                    default="",
                    tooltip=(
                        "Optional later scenes: one prompt per line, starting with clip 2. "
                        "Empty uses the opening prompt."
                    ),
                ),
                io.Image.Input(
                    "image",
                    display_name="Starting image",
                    optional=True,
                    tooltip="Optional first frame for the first clip.",
                ),
            ],
            outputs=[
                io.Video.Output(display_name="video"),
                io.Audio.Output(display_name="audio"),
                io.String.Output(display_name="metadata"),
            ],
            description=("Chain clips from their previous final frame and save one video with sound."),
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
