"""Register the connector's public ComfyUI nodes."""

from typing import override
import asyncio

from comfy_api.latest import ComfyExtension, io

from .runtime import initialize_runtime
from .comfy.routes import register_configuration
from .nodes.x2.edit import X2EditVideo
from .nodes.ltx.speak import LtxSpeak
from .nodes.sana.edit import SanaEditVideo
from .nodes.x2.webcam import X2Webcam
from .nodes.sana.webcam import SanaWebcam
from .nodes.fast.generate import FastGenerate
from .nodes.helios.prompt import HeliosAddPrompt
from .nodes.longlive.shot import LongLiveAddShot
from .nodes.visko.generate import ViskoGenerate
from .nodes.helios.generate import HeliosGenerate
from .nodes.lingbot.explore import LingBotExplore, LingBotWorldExplore
from .nodes.fast.continuation import FastContinue
from .nodes.longlive.generate import LongLiveGenerate

NODE_REGISTRATIONS: tuple[type[io.ComfyNode], ...] = (
    SanaWebcam,
    X2Webcam,
    FastGenerate,
    FastContinue,
    LtxSpeak,
    HeliosGenerate,
    HeliosAddPrompt,
    LingBotExplore,
    LingBotWorldExplore,
    LongLiveGenerate,
    LongLiveAddShot,
    SanaEditVideo,
    X2EditVideo,
    ViskoGenerate,
)


class ReactorExtension(ComfyExtension):
    """Own the connector's host registration."""

    @override
    async def on_load(self) -> None:
        """Initialize shared state and register local routes when ComfyUI loads the extension."""
        await asyncio.to_thread(initialize_runtime)
        register_configuration()

    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        """Return the node classes registered by this connector."""
        return list(NODE_REGISTRATIONS)
