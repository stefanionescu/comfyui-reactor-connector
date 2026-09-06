"""Continue a scene across several clips without queuing another ComfyUI run."""

import asyncio
from functools import partial

from comfy_api.latest import Input, io

from ..execution.continuous import FastContinueRequest
from ..media.file_output import owned_io
from ..media.images import image_png
from .controls import generation_controls
from .host import execute_video, operation_fingerprint, wait_for_execution


class FastContinue(io.ComfyNode):
    @classmethod
    async def fingerprint_inputs(cls, **kwargs: object) -> str:
        return await operation_fingerprint("fast-continue-v1")

    @classmethod
    def define_schema(cls) -> io.Schema:
        controls = generation_controls(
            "Follow a stream through a quiet forest. Water splashes softly."
        )
        controls[1] = io.Float.Input(
            "clip_seconds",
            display_name="Clip length (seconds)",
            default=6,
            min=5.167,
            max=14.375,
            step=0.001,
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
                    options=["16:9", "1:1", "9:16", "4:3"],
                    default="16:9",
                ),
                io.Int.Input(
                    "clip_count",
                    display_name="Number of clips",
                    default=3,
                    min=2,
                    max=8,
                    tooltip=(
                        "Total clips in one paid session. Their combined length must fit the "
                        "video duration limit."
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
            description=(
                "Chain clips from their previous final frame and save one video with sound."
            ),
        )

    @classmethod
    async def execute(
        cls,
        prompt: str,
        clip_seconds: float,
        seed: int,
        variation: int,
        aspect: str,
        clip_count: int,
        later_prompts: str,
        image: Input.Image | None = None,
    ) -> io.NodeOutput:
        async def generate() -> io.NodeOutput:
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
