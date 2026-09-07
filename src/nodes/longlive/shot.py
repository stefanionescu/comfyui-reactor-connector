"""Build and execute LongLive shots without making users write model commands."""

from comfy_api.latest import io
from ....config.prompts import DEFAULT_SHOT_PROMPT
from ...execution.storyboard import Shot, append_shot
from ....config.generation.prompts import MAX_SHOT_CHUNK, DEFAULT_TRANSITION, OPTIONS_TRANSITION


class LongLiveAddShot(io.ComfyNode):
    """Append one later shot without connecting to Reactor."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Declare the saved input names, controls, and output sockets for this node."""
        return io.Schema(
            node_id="ReactorIncLongLiveAddShot",
            display_name="Reactor LongLive: Add a shot",
            category="Reactor/Plans",
            inputs=[
                io.String.Input(
                    "previous",
                    display_name="Previous steps (JSON)",
                    default="[]",
                    multiline=False,
                    advanced=True,
                    tooltip="Leave [] for the first shot, or connect the previous shot node.",
                ),
                io.Int.Input(
                    "at_session_chunk",
                    display_name="Start chunk",
                    default=1,
                    min=1,
                    max=MAX_SHOT_CHUNK,
                    tooltip=("When this shot starts. Each chunk is 29 frames, about 1.2 seconds at 24 fps."),
                ),
                io.Combo.Input(
                    "transition",
                    display_name="Transition",
                    options=OPTIONS_TRANSITION,
                    default=DEFAULT_TRANSITION,
                    tooltip="Soft keeps the scene memory. Cut starts a new scene.",
                ),
                io.String.Input(
                    "prompt",
                    display_name="Scene prompt",
                    placeholder="Scene prompt",
                    default=DEFAULT_SHOT_PROMPT,
                    multiline=True,
                    tooltip="Describe this later shot.",
                ),
            ],
            outputs=[io.String.Output(display_name="storyboard")],
            description="Add a LongLive shot. This preparation node uses no credits.",
            search_aliases=["Reactor", "LongLive", "schedule", "storyboard"],
        )

    @classmethod
    def execute(  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        cls, *, previous: str, at_session_chunk: int, transition: str, prompt: str
    ) -> io.NodeOutput:
        """Validate and append one scheduled transition to the serialized storyboard."""
        return io.NodeOutput(append_shot(previous, Shot(at_session_chunk, transition, prompt)))
