"""Provide LingBot camera controls and video output in ComfyUI."""

import asyncio

from comfy_api.latest import Input, io

from ..execution.worlds import LingBotRequest, LingBotWorld2Request
from ..media.images import image_png
from .controls import generation_controls, video_outputs
from .host import execute_video, operation_fingerprint


def _directions(world2: bool) -> list[io.Input]:
    movement = ["idle", "forward", "back"]
    if not world2:
        movement.extend(["strafe_left", "strafe_right"])
    controls: list[io.Input] = [
        io.Combo.Input(
            "movement",
            display_name="Movement",
            options=movement,
            default="idle",
            tooltip="Keep moving in this direction while recording. Choose idle to stay in place.",
        ),
    ]
    if world2:
        controls.append(
            io.Combo.Input(
                "lateral",
                display_name="Sideways movement",
                options=["idle", "strafe_left", "strafe_right"],
                default="idle",
                tooltip="Sideways movement combines with forward or backward movement.",
            )
        )
    controls.extend(
        [
            io.Combo.Input(
                "look_horizontal",
                display_name="Turn left or right",
                options=["idle", "left", "right"],
                default="idle",
                tooltip="Keep turning the camera left or right while recording.",
            ),
            io.Combo.Input(
                "look_vertical",
                display_name="Look up or down",
                options=["idle", "up", "down"],
                default="idle",
                tooltip="Keep looking up or down while recording.",
            ),
            io.Float.Input(
                "rotation_speed_deg",
                display_name="Turn per step (degrees)",
                default=5.0,
                min=0.0,
                max=30.0,
                step=0.1,
                tooltip=(
                    "Turn amount per model step, in degrees. Larger values turn "
                    "faster; 0 stops turning."
                ),
            ),
        ]
    )
    return controls


def _schema(world2: bool) -> io.Schema:
    title = "LingBot World 2" if world2 else "LingBot"
    return io.Schema(
        node_id="ReactorIncLingBotWorld2Explore" if world2 else "ReactorIncLingBotExplore",
        display_name=f"Reactor {title}: Explore an image",
        category="Reactor/Worlds",
        inputs=[
            io.Image.Input(
                "image",
                display_name="Starting image",
                tooltip="Upload one image to use as the starting scene.",
            ),
            *generation_controls(),
            *_directions(world2),
            io.Boolean.Input(
                "interactive",
                display_name="Live controls",
                default=False,
                optional=True,
                tooltip=(
                    "Move with keys or buttons and edit the scene prompt. The camera starts still."
                ),
            ),
        ],
        outputs=video_outputs(),
        description=(
            "Move through a scene from your image and save a video. Choose how long to record."
        ),
        search_aliases=["Reactor", title, "camera", "world", "image to video"],
    )


class LingBotExplore(io.ComfyNode):
    """Record a LingBot scene using a starting image and camera directions."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return _schema(False)

    @classmethod
    async def fingerprint_inputs(cls, **kwargs: object) -> str:
        return await operation_fingerprint("lingbot-bounded-v1")

    @classmethod
    async def execute(
        cls,
        image: Input.Image,
        prompt: str,
        duration_seconds: float,
        seed: int,
        variation: int,
        movement: str,
        look_horizontal: str,
        look_vertical: str,
        rotation_speed_deg: float,
        interactive: bool = False,
    ) -> io.NodeOutput:
        encoded = await asyncio.to_thread(image_png, image)
        return await execute_video(
            LingBotRequest(
                prompt,
                duration_seconds,
                seed,
                encoded,
                "idle" if interactive else movement,
                "idle" if interactive else look_horizontal,
                "idle" if interactive else look_vertical,
                rotation_speed_deg,
            ),
            interactive=interactive,
            node_id=cls.define_schema().node_id,
        )


class LingBotWorld2Explore(io.ComfyNode):
    """Record World 2 with separate forward/back and sideways controls."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return _schema(True)

    @classmethod
    async def fingerprint_inputs(cls, **kwargs: object) -> str:
        return await operation_fingerprint("lingbot-world-2-bounded-v1")

    @classmethod
    async def execute(
        cls,
        image: Input.Image,
        prompt: str,
        duration_seconds: float,
        seed: int,
        variation: int,
        movement: str,
        lateral: str,
        look_horizontal: str,
        look_vertical: str,
        rotation_speed_deg: float,
        interactive: bool = False,
    ) -> io.NodeOutput:
        encoded = await asyncio.to_thread(image_png, image)
        return await execute_video(
            LingBotWorld2Request(
                prompt,
                duration_seconds,
                seed,
                encoded,
                "idle" if interactive else movement,
                "idle" if interactive else look_horizontal,
                "idle" if interactive else look_vertical,
                rotation_speed_deg,
                "idle" if interactive else lateral,
            ),
            interactive=interactive,
            node_id=cls.define_schema().node_id,
        )
