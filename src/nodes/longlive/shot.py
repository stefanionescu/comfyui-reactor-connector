"""Build and execute LongLive shots without making users write model commands."""

from comfy_api.latest import io
from ...language import translate
from ..schema import translate_schema
from ...execution.longlive.storyboard import Shot, append_shot
from ....config.generation.prompts import MAX_SHOT_CHUNK, DEFAULT_TRANSITION, OPTIONS_TRANSITION


class LongLiveAddShot(io.ComfyNode):
    """Append one later shot without connecting to Reactor."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the inputs and outputs saved in ComfyUI workflows."""
        return translate_schema(
            io.Schema(
                node_id="ReactorIncLongLiveAddShot",
                inputs=[
                    io.String.Input(
                        "previous",
                        default="[]",
                        multiline=False,
                        advanced=True,
                    ),
                    io.Int.Input(
                        "at_session_chunk",
                        default=1,
                        min=1,
                        max=MAX_SHOT_CHUNK,
                    ),
                    io.Combo.Input(
                        "transition",
                        options=OPTIONS_TRANSITION,
                        default=DEFAULT_TRANSITION,
                    ),
                    io.String.Input(
                        "prompt",
                        default=translate("prompts", "shot"),
                        multiline=True,
                    ),
                ],
                outputs=[io.String.Output()],
            )
        )

    @classmethod
    def execute(  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        cls, *, previous: str, at_session_chunk: int, transition: str, prompt: str
    ) -> io.NodeOutput:
        """Validate and append one scheduled transition to the serialized storyboard."""
        return io.NodeOutput(append_shot(previous, Shot(at_session_chunk, transition, prompt)))
