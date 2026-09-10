"""Expose LTX speech with a required native portrait and synchronized media."""

import asyncio
from ...media.output import owned_io
from ...media.images import image_png
from ..schema import translate_schema
from comfy_api.latest import io, Input
from ..controls import generation_controls
from ...execution.ltx.request import LtxSpeakRequest
from ...comfy.execution import execute_video, wait_for_execution, operation_fingerprint
from ....config.generation.speech import (
    DEFAULT_SCRIPT,
    MAX_WORDS_PER_MINUTE,
    MIN_WORDS_PER_MINUTE,
    DEFAULT_WORDS_PER_MINUTE,
)


class LtxSpeak(io.ComfyNode):
    """Animate one portrait speaking the supplied script."""

    @classmethod
    async def fingerprint_inputs(cls, **_kwargs: object) -> str:
        """Include current settings and model metadata in the ComfyUI cache key."""
        return await operation_fingerprint("ltx-speech-recording-v1")

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return translate_schema(
            io.Schema(
                node_id="ReactorIncLtxSpeak",
                inputs=[
                    *generation_controls("speech"),
                    io.String.Input(
                        "script",
                        multiline=True,
                        default=DEFAULT_SCRIPT,
                    ),
                    io.Int.Input(
                        "words_per_minute",
                        default=DEFAULT_WORDS_PER_MINUTE,
                        min=MIN_WORDS_PER_MINUTE,
                        max=MAX_WORDS_PER_MINUTE,
                    ),
                    io.Image.Input(
                        "image",
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
        duration_seconds: float,
        seed: int,
        variation: int,
        script: str,
        words_per_minute: int,
        image: Input.Image,
    ) -> io.NodeOutput:
        """Animate the portrait speaking the script and return video, audio, and recording details."""
        # ComfyUI uses variation to invalidate its cache; Reactor does not consume it.
        del variation

        async def generate() -> io.NodeOutput:
            """Prepare media inside the owned task before starting the Reactor session."""
            encoded = await owned_io(lambda: image_png(image))
            return await execute_video(
                LtxSpeakRequest(
                    prompt,
                    duration_seconds,
                    seed,
                    image=encoded,
                    script=script,
                    words_per_minute=words_per_minute,
                ),
                node_id=cls.define_schema().node_id,
            )

        return await wait_for_execution(asyncio.create_task(generate()))
