"""Register the connector's public ComfyUI nodes."""

import asyncio
from .nodes.ltx.speak import LtxSpeak
from .nodes.x2.webcam import X2Webcam
from .nodes.x2.edit import X2EditVideo
from .runtime import initialize_runtime
from .nodes.sana.webcam import SanaWebcam
from .nodes.sana.edit import SanaEditVideo
from .nodes.fast.generate import FastGenerate
from .nodes.visko.generate import ViskoGenerate
from comfy_api.latest import io, ComfyExtension
from .comfy.routes import register_configuration
from .nodes.helios.prompt import HeliosAddPrompt
from .nodes.longlive.shot import LongLiveAddShot
from .nodes.fast.continuation import FastContinue
from .nodes.helios.generate import HeliosGenerate
from .nodes.lingbot.explore import LingBotExplore
from .nodes.lingbot.world import LingBotWorldExplore
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

    async def on_load(self) -> None:
        """Initialize shared state and register local routes when ComfyUI loads the extension."""
        await asyncio.to_thread(initialize_runtime)
        register_configuration()

    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        """Return the node classes registered by this connector."""
        return list(NODE_REGISTRATIONS)
