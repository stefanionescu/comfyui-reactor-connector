"""Expose LTX speech with a required native portrait and synchronized media."""

from typing import Unpack, TypedDict, override
import asyncio
from functools import partial

from comfy_api.latest import Input, io

from ..base import VideoNode
from ..controls import build_inputs, build_outputs
from ...media.images import encode_png
from ...media.output import owned_io
from ...comfy.execution import generate_video, wait_for_execution
from ...state.generation.ltx import LtxSpeakRequest
from ...execution.ltx.operation import LtxSpeakOperation
from ...config.generation.speech import (
    DEFAULT_SCRIPT,
    MAX_WORDS_PER_MINUTE,
    MIN_WORDS_PER_MINUTE,
    DEFAULT_WORDS_PER_MINUTE,
)


class LtxSpeakInputs(TypedDict):
    """The saved inputs that ComfyUI passes to the LTX node, apart from the run number."""

    prompt: str
    duration_seconds: float
    seed: int
    script: str
    words_per_minute: int
    image: Input.Image


class LtxSpeak(VideoNode):
    """Animate one portrait speaking the supplied script."""

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return io.Schema(
            node_id='ReactorIncLtxSpeak',
            display_name='LTX: Make a Portrait Speak (Reactor)',
            description='Animate a portrait speaking a script and return video and separate audio.',
            category='Reactor/Generate',
            search_aliases=['Reactor', 'LTX', 'speech', 'talking portrait'],
            inputs=build_inputs(
                'speech',
                trailing=[
                    io.String.Input(
                        'script',
                        display_name='spoken words',
                        placeholder='spoken words',
                        multiline=True,
                        default=DEFAULT_SCRIPT,
                    ),
                    io.Int.Input(
                        'words_per_minute',
                        display_name='words per minute',
                        tooltip='Words spoken per minute. Reactor checks the supported range before generation.',
                        default=DEFAULT_WORDS_PER_MINUTE,
                        min=MIN_WORDS_PER_MINUTE,
                        max=MAX_WORDS_PER_MINUTE,
                    ),
                    io.Image.Input(
                        'image',
                        display_name='portrait image',
                        tooltip='One clear portrait with the whole head visible.',
                    ),
                ],
            ),
            outputs=build_outputs(has_audio=True),
        )

    @classmethod
    @override
    async def generate(cls, **inputs: Unpack[LtxSpeakInputs]) -> io.NodeOutput:
        """Animate the portrait speaking the script and return video and audio."""

        async def start() -> io.NodeOutput:
            """Prepare media inside the owned task before starting the Reactor session."""
            encoded = await owned_io(partial(encode_png, inputs['image']))
            request = LtxSpeakRequest(
                inputs['prompt'],
                inputs['duration_seconds'],
                inputs['seed'],
                image=encoded,
                script=inputs['script'],
                words_per_minute=inputs['words_per_minute'],
            )
            return await generate_video(LtxSpeakOperation(request))

        return await wait_for_execution(asyncio.create_task(start()))
