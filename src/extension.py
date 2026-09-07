"""Register the connector's public ComfyUI nodes."""

from .nodes.ltx import LtxSpeak
from .nodes.x2.webcam import X2Webcam
from .nodes.x2.edit import X2EditVideo
from .runtime import initialize_runtime
from .nodes.sana.webcam import SanaWebcam
from .nodes.sana.edit import SanaEditVideo
from .nodes.fast.generate import FastGenerate
from .nodes.helios.animate import HeliosAnimate
from comfy_api.latest import io, ComfyExtension
from .nodes.helios.prompt import HeliosAddPrompt
from .nodes.longlive.shot import LongLiveAddShot
from .nodes.fast.continuation import FastContinue
from .nodes.helios.generate import HeliosGenerate
from .nodes.helios.sequence import HeliosSequence
from .nodes.lingbot.explore import LingBotExplore
from .nodes.visko.stable import ViskoStableGenerate
from .nodes.lingbot.world import LingBotWorld2Explore
from .nodes.longlive.generate import LongLiveGenerate
from .nodes.visko.dynamic import ViskoDynamicGenerate
from .nodes.configuration import register_configuration
from .nodes.longlive.storyboard import LongLiveStoryboard


class ReactorExtension(ComfyExtension):
    """Own the connector's host registration."""

    async def on_load(self) -> None:
        """Initialize shared state and register local routes when ComfyUI loads the extension."""
        initialize_runtime()
        register_configuration()

    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        """Return the node classes registered by this connector."""
        return [
            SanaWebcam,
            X2Webcam,
            FastGenerate,
            FastContinue,
            LtxSpeak,
            HeliosGenerate,
            HeliosAnimate,
            HeliosAddPrompt,
            HeliosSequence,
            LingBotExplore,
            LingBotWorld2Explore,
            LongLiveGenerate,
            LongLiveStoryboard,
            LongLiveAddShot,
            SanaEditVideo,
            X2EditVideo,
            ViskoStableGenerate,
            ViskoDynamicGenerate,
        ]
