"""Append a shot to a LongLive storyboard without generating video."""

from comfy_api.latest import io
from ...state.generation.longlive import Shot
from ...execution.longlive.storyboard import append_shot
from ....config.generation.prompts import MAX_SHOT_CHUNK, DEFAULT_TRANSITION, OPTIONS_TRANSITION, DEFAULT_PROMPTS


class LongLiveAddShot(io.ComfyNode):
    """Append one later shot without connecting to Reactor."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return io.Schema(
            node_id="ReactorIncLongLiveAddShot",
            display_name="LongLive: Add a Shot (Reactor)",
            description="Add a shot to a LongLive storyboard.",
            category="Reactor/Plans",
            search_aliases=["Reactor", "LongLive", "schedule", "storyboard"],
            inputs=[
                io.String.Input(
                    "previous",
                    display_name="previous shots (JSON)",
                    tooltip="Leave [] for the first shot, or connect the previous shot node.",
                    default="[]",
                    multiline=False,
                    advanced=True,
                ),
                io.Int.Input(
                    "at_session_chunk",
                    display_name="start chunk",
                    tooltip="When this shot starts. Each chunk is 29 frames, about 1.2 seconds at 24 fps.",
                    default=1,
                    min=1,
                    max=MAX_SHOT_CHUNK,
                ),
                io.Combo.Input(
                    "transition",
                    display_name="transition",
                    tooltip="Soft transition continues from the preceding scene. Hard cut starts a new scene.",
                    options=OPTIONS_TRANSITION,
                    default=DEFAULT_TRANSITION,
                ),
                io.String.Input(
                    "prompt",
                    display_name="scene prompt",
                    placeholder="scene prompt",
                    tooltip="Describe this later shot.",
                    default=DEFAULT_PROMPTS["shot"],
                    multiline=True,
                ),
            ],
            outputs=[io.String.Output(display_name="shots")],
        )

    @classmethod
    def execute(  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        cls, *, previous: str, at_session_chunk: int, transition: str, prompt: str
    ) -> io.NodeOutput:
        """Validate and append one scheduled transition to the serialized storyboard."""
        return io.NodeOutput(append_shot(previous, Shot(at_session_chunk, transition, prompt)))
