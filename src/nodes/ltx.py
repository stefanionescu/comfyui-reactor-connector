"""Expose LTX speech with a required native portrait and synchronized media."""

import asyncio
from ..media.output import owned_io
from ..media.images import image_png
from comfy_api.latest import io, Input
from .controls import generation_controls
from ..execution.ltx import LtxSpeakRequest
from ...config.prompts import VIDEO_LTX_PROMPT
from .host import execute_video, wait_for_execution, operation_fingerprint
from ...config.generation.speech import DEFAULT_SCRIPT, MAX_WORDS_PER_MINUTE, DEFAULT_WORDS_PER_MINUTE


class LtxSpeak(io.ComfyNode):
    """Animate one portrait speaking the supplied script."""

    @classmethod
    async def fingerprint_inputs(cls, **_kwargs: object) -> str:
        """Include current settings and model metadata in the ComfyUI cache key."""
        return await operation_fingerprint("ltx-speech-recording-v1")

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Declare the saved input names, controls, and output sockets for this node."""
        return io.Schema(
            node_id="ReactorIncLtxSpeak",
            display_name="Reactor LTX: Make a portrait speak",
            category="Reactor/Generate",
            inputs=[
                *generation_controls(VIDEO_LTX_PROMPT),
                io.String.Input(
                    "script",
                    display_name="Spoken words",
                    placeholder="Spoken words",
                    multiline=True,
                    default=DEFAULT_SCRIPT,
                ),
                io.Int.Input(
                    "words_per_minute",
                    display_name="Words per minute",
                    default=DEFAULT_WORDS_PER_MINUTE,
                    min=1,
                    max=MAX_WORDS_PER_MINUTE,
                    tooltip=("Words spoken per minute. Reactor checks the supported range before generation."),
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
            description=("Animate a portrait speaking a script. Help explains framing, duration, and sound."),
            search_aliases=["Reactor", "LTX", "speech", "talking portrait"],
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
