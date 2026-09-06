"""Expose LTX speech with a required native portrait and synchronized media."""

import asyncio

from comfy_api.latest import Input, io

from ..execution.ltx import LtxSpeakRequest
from ..media.file_output import owned_io
from ..media.images import image_png
from .controls import generation_controls
from .host import execute_video, operation_fingerprint, wait_for_execution


class LtxSpeak(io.ComfyNode):
    """Animate one portrait speaking the supplied script."""

    @classmethod
    async def fingerprint_inputs(cls, **kwargs: object) -> str:
        return await operation_fingerprint("ltx-speech-recording-v1")

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="ReactorIncLtxSpeak",
            display_name="Reactor LTX: Make a portrait speak",
            category="Reactor/Generate",
            inputs=[
                *generation_controls("A person faces the camera and speaks calmly."),
                io.String.Input(
                    "script",
                    display_name="Spoken words",
                    placeholder="Spoken words",
                    multiline=True,
                    default="Hello. Welcome to this short video.",
                ),
                io.Int.Input(
                    "words_per_minute",
                    display_name="Words per minute",
                    default=140,
                    min=1,
                    max=1000,
                    tooltip=(
                        "Words spoken per minute. "
                        "Reactor checks the supported range before generation."
                    ),
                ),
                io.Image.Input(
                    "image",
                    display_name="Starting image",
                    tooltip="One clear portrait with the whole head visible.",
                ),
            ],
            outputs=[
                io.Video.Output(display_name="video"),
                io.Audio.Output(display_name="audio"),
                io.String.Output(display_name="metadata"),
            ],
            description=(
                "Animate a portrait speaking a script. Help explains framing, duration, and sound."
            ),
            search_aliases=["Reactor", "LTX", "speech", "talking portrait"],
        )

    @classmethod
    async def execute(
        cls,
        prompt: str,
        duration_seconds: float,
        seed: int,
        variation: int,
        script: str,
        words_per_minute: int,
        image: Input.Image,
    ) -> io.NodeOutput:
        async def generate() -> io.NodeOutput:
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
