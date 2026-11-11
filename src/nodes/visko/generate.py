"""Generate Visko Stable or Dynamic video with synchronized audio."""

from typing import override
import asyncio

from comfy_api.latest import Input, io

from ..base import VideoNode
from ..controls import build_inputs, build_outputs
from ...media.images import encode_png
from ...media.output import owned_io
from ...comfy.execution import generate_video, wait_for_execution
from ...state.generation.visko import ViskoRequest
from ...execution.visko.operation import ViskoStableOperation, ViskoDynamicOperation

# Both Visko deployments take the same inputs; the model choice selects one.
OPERATIONS: dict[str, type[ViskoStableOperation]] = {
    'stable': ViskoStableOperation,
    'dynamic': ViskoDynamicOperation,
}


class ViskoGenerate(VideoNode):
    """Generate video and sound from a prompt and an optional starting image."""

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows.

        Returns:
            The schema of the node.

        """
        return io.Schema(
            node_id='ReactorIncViskoGenerate',
            display_name='Visko: Generate Video (Reactor)',
            description='Generate video with sound from text or a starting image.',
            category='Reactor/Generate',
            search_aliases=['Reactor', 'Visko', 'audio', 'image to video'],
            inputs=build_inputs(
                'visko',
                leading=[
                    io.Combo.Input(
                        'model',
                        display_name='model',
                        tooltip="Choose Reactor's Visko Orbis Stable or Dynamic version. Both take the same inputs.",
                        options=list(OPERATIONS),
                        default='stable',
                    ),
                ],
                trailing=[
                    io.String.Input(
                        'audio_prompt',
                        display_name='audio prompt',
                        placeholder='audio prompt',
                        tooltip='Describe the sound briefly, or leave blank to use the picture.',
                        default='',
                        multiline=True,
                    ),
                    io.String.Input(
                        'resolution',
                        display_name='resolution',
                        default='',
                        tooltip='Leave blank for default, or use an offered resolution name.',
                    ),
                    io.Boolean.Input(
                        'audio_enabled',
                        display_name='generate audio',
                        default=True,
                        tooltip="Generate sound. When false, the model's audio track is silent.",
                    ),
                    io.Boolean.Input(
                        'prompt_passthrough',
                        display_name='use prompt unchanged',
                        default=False,
                        tooltip='Use your exact prompt without Reactor preparing it first.',
                    ),
                    io.Image.Input(
                        'image',
                        display_name='starting image',
                        optional=True,
                        tooltip='Optional single RGB starting image.',
                    ),
                ],
                is_live=True,
            ),
            outputs=build_outputs(has_audio=True),
        )

    @classmethod
    @override
    async def generate(
        cls,
        *,
        model: str,
        prompt: str,
        duration_seconds: float,
        seed: int,
        audio_prompt: str,
        resolution: str,
        audio_enabled: bool,
        prompt_passthrough: bool,
        image: Input.Image | None = None,
        interactive: bool = False,
    ) -> io.NodeOutput:
        """Generate Visko video and audio from the selected text, image, and sound controls.

        Args:
            model: The name of the Visko version to run.
            prompt: The scene prompt of the video.
            duration_seconds: The requested video length in seconds.
            seed: The seed that the model generates from.
            audio_prompt: The description of the sound.
            resolution: The name of the resolution, or an empty string for the default.
            audio_enabled: Whether the model generates sound.
            prompt_passthrough: Whether Reactor uses the prompt unchanged.
            image: The optional starting image.
            interactive: Whether to open the live controls.

        Returns:
            The video and its sound.

        """

        async def start() -> io.NodeOutput:
            """Prepare media inside the owned task before starting the Reactor session.

            Returns:
                The output of the session.

            """
            source_image = image
            encoded = None if source_image is None else await owned_io(lambda: encode_png(source_image))
            request = ViskoRequest(
                prompt,
                duration_seconds,
                seed,
                image=encoded,
                audio_prompt=audio_prompt,
                resolution=resolution,
                audio_enabled=audio_enabled,
                prompt_passthrough=prompt_passthrough,
            )
            return await generate_video(
                OPERATIONS[model](request),
                interactive=interactive,
            )

        return await wait_for_execution(asyncio.create_task(start()))
