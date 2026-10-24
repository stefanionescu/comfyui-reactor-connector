"""Record edits from a camera explicitly enabled in the owning browser."""

from typing import Unpack, TypedDict, NotRequired, override
import asyncio
from functools import partial

from comfy_api.latest import Input, io

from ..base import VideoNode
from ..controls import build_inputs, build_outputs
from ...config.nodes import (
    MAX_WEBCAM_SECONDS,
    MIN_WEBCAM_SECONDS,
    STEP_WEBCAM_SECONDS,
    DEFAULT_WEBCAM_SECONDS,
    DEFAULT_POINTER_POSITION,
)
from ...media.images import encode_png
from ...media.output import owned_io
from ...media.webcam import WebcamFrames
from ...comfy.execution import generate_video, wait_for_execution
from ...comfy.interaction import build_live_options
from ...state.generation.x2 import X2Request
from ...execution.x2.operation import X2Operation


class X2WebcamInputs(TypedDict):
    """The saved inputs that ComfyUI passes to the X2 webcam node, apart from the run number."""

    prompt: str
    duration_seconds: float
    reference_image: NotRequired[Input.Image | None]


class X2Webcam(VideoNode):
    """Open X2 webcam and dragging controls and record the resulting video."""

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return io.Schema(
            node_id='ReactorIncX2Webcam',
            display_name='X2: Edit Webcam Video (Reactor)',
            description='Edit webcam video and drag on the output to steer the subject.',
            category='Reactor/Live',
            search_aliases=[],
            inputs=build_inputs(
                'webcam',
                duration=io.Float.Input(
                    'duration_seconds',
                    display_name='video duration (seconds)',
                    default=DEFAULT_WEBCAM_SECONDS,
                    min=MIN_WEBCAM_SECONDS,
                    max=MAX_WEBCAM_SECONDS,
                    step=STEP_WEBCAM_SECONDS,
                ),
                trailing=[
                    io.Image.Input(
                        'reference_image',
                        display_name='reference image',
                        optional=True,
                        tooltip='Optional picture of a subject to insert or replace.',
                    ),
                ],
                has_seed=False,
            ),
            outputs=build_outputs(has_audio=False),
        )

    @classmethod
    @override
    async def generate(cls, **inputs: Unpack[X2WebcamInputs]) -> io.NodeOutput:
        """Open X2 webcam and dragging controls and record the resulting video."""
        reference_image = inputs.get('reference_image')

        async def start() -> io.NodeOutput:
            """Prepare media inside the owned task before starting the Reactor session."""
            camera = WebcamFrames()
            try:
                image = None if reference_image is None else await owned_io(partial(encode_png, reference_image))
                request = X2Operation(
                    X2Request(
                        inputs['prompt'],
                        inputs['duration_seconds'],
                        0,
                        image=image,
                        pointer_x=DEFAULT_POINTER_POSITION,
                        pointer_y=DEFAULT_POINTER_POSITION,
                    ),
                    webcam=camera,
                )
                return await generate_video(request, controls=build_live_options(request, webcam=camera))
            finally:
                await camera.close()

        return await wait_for_execution(asyncio.create_task(start()))
