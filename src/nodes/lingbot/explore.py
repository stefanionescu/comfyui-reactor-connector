"""Record a LingBot or LingBot World 2 scene from an image and camera directions."""

from typing import Unpack, override

from comfy_api.latest import io

from ..base import VideoNode
from .schema import LingBotInputs, LingBotWorldInputs, lingbot_inputs, build_operation
from ..controls import build_outputs
from ...comfy.execution import generate_video


class LingBotExplore(VideoNode):
    """Record a LingBot scene using a starting image and camera directions."""

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows.

        Returns:
            The schema of the node.

        """
        return io.Schema(
            node_id='ReactorIncLingBotExplore',
            display_name='LingBot: Explore an Image (Reactor)',
            description='Move through a scene from your image and save a video. Choose how long to record.',
            category='Reactor/Worlds',
            search_aliases=['Reactor', 'LingBot', 'camera', 'world', 'image to video'],
            inputs=lingbot_inputs(is_world_two=False),
            outputs=build_outputs(has_audio=False),
        )

    @classmethod
    @override
    async def generate(cls, **inputs: Unpack[LingBotInputs]) -> io.NodeOutput:
        """Explore the starting image with the selected LingBot camera controls.

        Args:
            **inputs: The saved inputs of the LingBot node.

        Returns:
            The recorded video.

        """
        interactive = inputs.get('interactive', False)
        operation = await build_operation(inputs, interactive=interactive, lateral=None)
        return await generate_video(operation, interactive=interactive)


class LingBotWorldExplore(VideoNode):
    """Record World 2 with separate forward/back and sideways controls."""

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows.

        Returns:
            The schema of the node.

        """
        return io.Schema(
            node_id='ReactorIncLingBotWorld2Explore',
            display_name='LingBot World 2: Explore an Image (Reactor)',
            description='Move through a scene from your image and save a video. Choose how long to record.',
            category='Reactor/Worlds',
            search_aliases=['Reactor', 'LingBot World 2', 'camera', 'world', 'image to video'],
            inputs=lingbot_inputs(is_world_two=True),
            outputs=build_outputs(has_audio=False),
        )

    @classmethod
    @override
    async def generate(cls, **inputs: Unpack[LingBotWorldInputs]) -> io.NodeOutput:
        """Explore the starting image with LingBot World 2 movement and camera controls.

        Args:
            **inputs: The saved inputs of the LingBot World 2 node.

        Returns:
            The recorded video.

        """
        interactive = inputs.get('interactive', False)
        operation = await build_operation(inputs, interactive=interactive, lateral=inputs['lateral'])
        return await generate_video(operation, interactive=interactive)
