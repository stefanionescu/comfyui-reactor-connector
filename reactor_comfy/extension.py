"""Register the connector's public ComfyUI nodes."""

from comfy_api.latest import ComfyExtension, io

from .nodes.configuration import register_configuration
from .nodes.continuous import FastContinue
from .nodes.fast import FastGenerate
from .nodes.helios import HeliosAnimate, HeliosGenerate
from .nodes.ltx import LtxSpeak
from .nodes.prompt_sequence import HeliosAddPrompt, HeliosSequence
from .nodes.sana import SanaEditVideo
from .nodes.storyboard import LongLiveAddShot, LongLiveGenerate, LongLiveStoryboard
from .nodes.visko import ViskoDynamicGenerate, ViskoStableGenerate
from .nodes.webcam import SanaWebcam, X2Webcam
from .nodes.worlds import LingBotExplore, LingBotWorld2Explore
from .nodes.x2 import X2EditVideo
from .runtime import initialize_runtime


class ReactorExtension(ComfyExtension):
    """Own the connector's host registration."""

    async def on_load(self) -> None:
        initialize_runtime()
        register_configuration()

    async def get_node_list(self) -> list[type[io.ComfyNode]]:
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
