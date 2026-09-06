"""Build and execute LongLive shots without making users write model commands."""

from comfy_api.latest import io

from ..execution.storyboard import LongLiveRequest, Shot, append_shot, parse_storyboard
from .controls import generation_controls, live_control, video_outputs
from .host import execute_video, operation_fingerprint


class LongLiveGenerate(io.ComfyNode):
    """Start a LongLive scene from its opening shot prompt."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="ReactorIncLongLiveGenerate",
            display_name="Reactor LongLive: Generate video",
            category="Reactor/Generate",
            inputs=[*generation_controls(), live_control()],
            outputs=video_outputs(),
            description="Generate a short LongLive scene from an opening shot prompt.",
            search_aliases=["Reactor", "LongLive", "text to video"],
        )

    @classmethod
    async def fingerprint_inputs(cls, **kwargs: object) -> str:
        return await operation_fingerprint("longlive-bounded-v1")

    @classmethod
    async def execute(
        cls,
        prompt: str,
        duration_seconds: float,
        seed: int,
        variation: int,
        interactive: bool = False,
    ) -> io.NodeOutput:
        return await execute_video(
            LongLiveRequest(prompt, duration_seconds, seed),
            interactive=interactive,
            node_id=cls.define_schema().node_id,
        )


class LongLiveStoryboard(io.ComfyNode):
    """Prepare scheduled soft shots and hard cuts before generation starts."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="ReactorIncLongLiveStoryboard",
            display_name="Reactor LongLive: Create a storyboard",
            category="Reactor/Generate",
            inputs=[
                *generation_controls(),
                io.String.Input(
                    "storyboard",
                    display_name="Shots (JSON)",
                    default="[]",
                    multiline=False,
                    advanced=True,
                    tooltip="Connect Reactor LongLive: Add a shot, or enter a validated shot list.",
                ),
            ],
            outputs=video_outputs(),
            description="Generate an opening shot and schedule later shots by chunk number.",
            search_aliases=["Reactor", "LongLive", "shots", "cuts"],
        )

    @classmethod
    async def fingerprint_inputs(cls, **kwargs: object) -> str:
        return await operation_fingerprint("longlive-storyboard-v1")

    @classmethod
    async def execute(
        cls,
        prompt: str,
        duration_seconds: float,
        seed: int,
        variation: int,
        storyboard: str,
    ) -> io.NodeOutput:
        shots = parse_storyboard(storyboard)
        return await execute_video(
            LongLiveRequest(prompt, duration_seconds, seed, shots=shots),
            node_id=cls.define_schema().node_id,
        )


class LongLiveAddShot(io.ComfyNode):
    """Append one later shot without connecting to Reactor."""

    @classmethod
    def define_schema(cls) -> io.Schema:
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
                    max=100_000,
                    tooltip=(
                        "When this shot starts. Each chunk is 29 frames, "
                        "about 1.2 seconds at 24 fps."
                    ),
                ),
                io.Combo.Input(
                    "transition",
                    display_name="Transition",
                    options=["soft", "cut"],
                    default="soft",
                    tooltip="Soft keeps the scene memory. Cut starts a new scene.",
                ),
                io.String.Input(
                    "prompt",
                    display_name="Scene prompt",
                    placeholder="Scene prompt",
                    default="The camera pulls back to reveal the surrounding landscape.",
                    multiline=True,
                    tooltip="Describe this later shot.",
                ),
            ],
            outputs=[io.String.Output(display_name="storyboard")],
            description="Add a LongLive shot. This preparation node uses no credits.",
            search_aliases=["Reactor", "LongLive", "schedule", "storyboard"],
        )

    @classmethod
    def execute(
        cls, previous: str, at_session_chunk: int, transition: str, prompt: str
    ) -> io.NodeOutput:
        return io.NodeOutput(append_shot(previous, Shot(at_session_chunk, transition, prompt)))
