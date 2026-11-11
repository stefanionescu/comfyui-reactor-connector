"""Generate a Helios video from a prompt, an optional starting image, and optional scheduled prompts."""

from typing import override
import asyncio

from comfy_api.latest import Input, io

from ..base import VideoNode
from ...errors import ErrorCode, ConnectorError
from ..controls import build_inputs, build_outputs
from ...media.images import encode_png
from ...comfy.execution import generate_video
from ...config.messages.inputs import LIVE_CONTROLS_SEQUENCE
from ...state.generation.helios import HeliosRequest
from ...execution.helios.prompts import parse_sequence
from ...execution.helios.operation import HeliosOperation


class HeliosGenerate(VideoNode):
    """Generate a video from a prompt, an optional starting image, and an optional prompt sequence."""

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows.

        Returns:
            The schema of the node.

        """
        return io.Schema(
            node_id='ReactorIncHeliosGenerate',
            display_name='Helios: Generate Video (Reactor)',
            category='Reactor/Generate',
            description='Generate a video from a scene prompt, with an optional starting image and prompt sequence.',
            search_aliases=['Reactor', 'Helios', 'text to video', 'image to video', 'prompt sequence'],
            inputs=build_inputs(
                trailing=[
                    io.String.Input(
                        'sequence',
                        display_name='prompt sequence (JSON)',
                        tooltip='Optionally connect Reactor Helios: Add a Prompt. [] keeps the opening prompt.',
                        default='[]',
                        multiline=False,
                        advanced=True,
                    ),
                    io.Image.Input(
                        'image',
                        display_name='starting image',
                        tooltip='Optionally connect one starting RGB image.',
                        optional=True,
                    ),
                ],
                is_live=True,
            ),
            outputs=build_outputs(has_audio=False),
        )

    @classmethod
    @override
    async def generate(
        cls,
        *,
        prompt: str,
        duration_seconds: float,
        seed: int,
        sequence: str,
        image: Input.Image | None = None,
        interactive: bool = False,
    ) -> io.NodeOutput:
        """Generate a Helios video from the opening prompt, scheduled prompts, or live changes.

        Args:
            prompt: The opening scene prompt.
            duration_seconds: The requested video length in seconds.
            seed: The seed that the model generates from.
            sequence: The scheduled prompts as JSON text.
            image: The optional starting image.
            interactive: Whether to open the live controls.

        Returns:
            The generated video.

        Raises:
            ConnectorError: When the node has both scheduled prompts and live controls.

        """
        prompts = parse_sequence(sequence)
        if prompts and interactive:
            raise ConnectorError(ErrorCode.INVALID_INPUT, LIVE_CONTROLS_SEQUENCE)
        encoded = await asyncio.to_thread(encode_png, image) if image is not None else None
        return await generate_video(
            HeliosOperation(HeliosRequest(prompt, duration_seconds, seed, image=encoded, prompts=prompts)),
            interactive=interactive,
        )
