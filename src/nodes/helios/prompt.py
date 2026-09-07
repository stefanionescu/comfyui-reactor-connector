"""Build a Helios prompt sequence using ordinary ComfyUI connections."""

from comfy_api.latest import io
from ....config.prompts import DEFAULT_FOREST_PROMPT
from ....config.generation.prompts import MAX_PROMPT_CHUNK
from ...execution.prompts import append_prompt, ScheduledPrompt


class HeliosAddPrompt(io.ComfyNode):
    """Add one later prompt without opening a Reactor session."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Declare the saved input names, controls, and output sockets for this node."""
        return io.Schema(
            node_id="ReactorIncHeliosAddPrompt",
            display_name="Reactor Helios: Add a prompt",
            category="Reactor/Plans",
            inputs=[
                io.String.Input(
                    "previous",
                    display_name="Previous steps (JSON)",
                    default="[]",
                    multiline=False,
                    advanced=True,
                    tooltip="Leave [] for the first later prompt, or connect the previous builder.",
                ),
                io.Int.Input(
                    "chunk",
                    display_name="Start chunk",
                    default=1,
                    min=1,
                    max=MAX_PROMPT_CHUNK,
                    tooltip="When this prompt starts. A Helios chunk contains 33 frames.",
                ),
                io.String.Input(
                    "prompt",
                    display_name="Scene prompt",
                    placeholder="Scene prompt",
                    default=DEFAULT_FOREST_PROMPT,
                    multiline=True,
                    tooltip="Describe the scene and motion after this change.",
                ),
            ],
            outputs=[io.String.Output(display_name="sequence")],
            description="Add a later Helios prompt. Preparing the sequence uses no credits.",
            search_aliases=["Reactor", "Helios", "schedule", "prompt"],
        )

    @classmethod
    def execute(  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        cls, *, previous: str, chunk: int, prompt: str
    ) -> io.NodeOutput:
        """Validate and append one scheduled prompt to the serialized sequence."""
        return io.NodeOutput(append_prompt(previous, ScheduledPrompt(chunk, prompt)))
