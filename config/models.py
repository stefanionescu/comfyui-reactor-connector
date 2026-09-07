"""Static models values used by the connector."""

NODE_MODELS = {
    "ReactorIncFastContinue": "fast-h3",
    "ReactorIncSanaWebcam": "sana-streaming",
    "ReactorIncX2Webcam": "x2",
    "ReactorIncFastGenerate": "fast-h3",
    "ReactorIncLtxSpeak": "ltx2",
    "ReactorIncHeliosGenerate": "helios",
    "ReactorIncHeliosAnimate": "helios",
    "ReactorIncHeliosAddPrompt": "helios",
    "ReactorIncHeliosSequence": "helios",
    "ReactorIncLingBotExplore": "lingbot",
    "ReactorIncLingBotWorld2Explore": "lingbot-world-2",
    "ReactorIncLongLiveGenerate": "longlive-v2",
    "ReactorIncLongLiveStoryboard": "longlive-v2",
    "ReactorIncLongLiveAddShot": "longlive-v2",
    "ReactorIncSanaEditVideo": "sana-streaming",
    "ReactorIncX2EditVideo": "x2",
    "ReactorIncViskoStableGenerate": "visko-orbis-stable",
    "ReactorIncViskoDynamicGenerate": "visko-orbis-dynamic",
}

IDENTITIES = {
    "fast-h3": ("fast-h3", "reactor/fast-h3"),
    "visko-orbis-stable": ("visko-orbis-stable", "reactor/visko-orbis-stable"),
    "visko-orbis-dynamic": ("visko-orbis-dynamic", "reactor/visko-orbis-dynamic"),
    "helios": ("helios", "reactor/helios"),
    "lingbot": ("lingbot", "reactor/lingbot"),
    "lingbot-world-2": ("lingbot-world-2", "reactor/lingbot-world-2"),
    "longlive-v2": ("longlive-v2", "reactor/longlive-v2"),
    "sana-streaming": ("sana-streaming", "reactor/sana-streaming"),
    "ltx2": ("ltx", "reactor/ltx2"),
    "x2": ("x2", "xmax/x2"),
}

MODEL_TITLES = {
    "fast-h3": "Fast H3",
    "visko-orbis-stable": "Visko Stable",
    "visko-orbis-dynamic": "Visko Dynamic",
}
