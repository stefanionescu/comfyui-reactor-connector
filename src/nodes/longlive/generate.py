"""Generate a LongLive scene from an opening shot prompt and optional scheduled shots."""

from typing import Unpack, TypedDict, NotRequired, override

from comfy_api.latest import io

from ..base import VideoNode
from ...errors import ErrorCode, ConnectorError
from ..controls import build_inputs, build_outputs
from ...comfy.execution import generate_video
from ...config.messages.inputs import LIVE_CONTROLS_STORYBOARD
from ...state.generation.longlive import LongLiveRequest
from ...execution.longlive.operation import LongLiveOperation
from ...execution.longlive.storyboard import parse_storyboard


class LongLiveInputs(TypedDict):
    """The saved inputs that ComfyUI passes to the LongLive node, apart from the run number."""

    prompt: str
    duration_seconds: float
    seed: int
    storyboard: str
    interactive: NotRequired[bool]


class LongLiveGenerate(VideoNode):
    """Start a LongLive scene from its opening shot prompt, with optional later shots."""

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return io.Schema(
            node_id='ReactorIncLongLiveGenerate',
            display_name='LongLive: Generate Video (Reactor)',
            description='Generate a LongLive scene from an opening shot prompt, with optional scheduled shots.',
            category='Reactor/Generate',
            search_aliases=['Reactor', 'LongLive', 'text to video', 'shots', 'cuts'],
            inputs=build_inputs(
                trailing=[
                    io.String.Input(
                        'storyboard',
                        display_name='shots (JSON)',
                        tooltip='Optionally connect Reactor LongLive: Add a Shot. [] keeps the opening shot.',
                        default='[]',
                        multiline=False,
                        advanced=True,
                    ),
                ],
                is_live=True,
            ),
            outputs=build_outputs(has_audio=False),
        )

    @classmethod
    @override
    async def generate(cls, **inputs: Unpack[LongLiveInputs]) -> io.NodeOutput:
        """Generate a LongLive video from the opening shot, scheduled shots, or live changes."""
        shots = parse_storyboard(inputs['storyboard'])
        interactive = inputs.get('interactive', False)
        if shots and interactive:
            raise ConnectorError(ErrorCode.INVALID_INPUT, LIVE_CONTROLS_STORYBOARD)
        request = LongLiveRequest(inputs['prompt'], inputs['duration_seconds'], inputs['seed'], shots=shots)
        return await generate_video(LongLiveOperation(request), interactive=interactive)
