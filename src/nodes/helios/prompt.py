"""Build a Helios prompt sequence using ordinary ComfyUI connections."""

from comfy_api.latest import io
from ...execution.helios.prompts import append_prompt
from ...state.generation.helios import ScheduledPrompt
from ....config.generation.prompts import MAX_PROMPT_CHUNK, DEFAULT_PROMPTS


class HeliosAddPrompt(io.ComfyNode):
    """Add one later prompt without opening a Reactor session."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return io.Schema(
            node_id="ReactorIncHeliosAddPrompt",
            display_name="Helios: Add a Prompt (Reactor)",
            description="Add a later prompt to a Helios sequence.",
            category="Reactor/Plans",
            search_aliases=["Reactor", "Helios", "schedule", "prompt"],
            inputs=[
                io.String.Input(
                    "previous",
                    display_name="previous prompts (JSON)",
                    tooltip="Leave [] for the first later prompt, or connect the previous Add a Prompt node.",
                    default="[]",
                    multiline=False,
                    advanced=True,
                ),
                io.Int.Input(
                    "chunk",
                    display_name="start chunk",
                    tooltip="When this prompt starts. A Helios chunk contains 33 frames.",
                    default=1,
                    min=1,
                    max=MAX_PROMPT_CHUNK,
                ),
                io.String.Input(
                    "prompt",
                    display_name="scene prompt",
                    placeholder="scene prompt",
                    tooltip="Describe the scene and motion after this change.",
                    default=DEFAULT_PROMPTS["forest"],
                    multiline=True,
                ),
            ],
            outputs=[io.String.Output(display_name="prompt sequence")],
        )

    @classmethod
    def execute(  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        cls, *, previous: str, chunk: int, prompt: str
    ) -> io.NodeOutput:
        """Validate and append one scheduled prompt to the serialized sequence."""
        return io.NodeOutput(append_prompt(previous, ScheduledPrompt(chunk, prompt)))
