"""Build a Helios prompt sequence using ordinary ComfyUI connections."""

from comfy_api.latest import io
from ...language import translate
from ..schema import translate_schema
from ....config.generation.prompts import MAX_PROMPT_CHUNK
from ...execution.helios.prompts import append_prompt, ScheduledPrompt


class HeliosAddPrompt(io.ComfyNode):
    """Add one later prompt without opening a Reactor session."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return translate_schema(
            io.Schema(
                node_id="ReactorIncHeliosAddPrompt",
                inputs=[
                    io.String.Input(
                        "previous",
                        default="[]",
                        multiline=False,
                        advanced=True,
                    ),
                    io.Int.Input(
                        "chunk",
                        default=1,
                        min=1,
                        max=MAX_PROMPT_CHUNK,
                    ),
                    io.String.Input(
                        "prompt",
                        default=translate("prompts", "forest"),
                        multiline=True,
                    ),
                ],
                outputs=[io.String.Output()],
            )
        )

    @classmethod
    def execute(  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        cls, *, previous: str, chunk: int, prompt: str
    ) -> io.NodeOutput:
        """Validate and append one scheduled prompt to the serialized sequence."""
        return io.NodeOutput(append_prompt(previous, ScheduledPrompt(chunk, prompt)))
