"""Match public model names to documentation and Reactor connection names."""

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
    "helios": "Helios",
    "lingbot": "LingBot",
    "lingbot-world-2": "LingBot World 2",
    "longlive-v2": "LongLive",
    "sana-streaming": "SANA",
    "ltx2": "LTX",
    "x2": "X2",
    "fast-h3": "Fast H3",
    "visko-orbis-stable": "Visko Stable",
    "visko-orbis-dynamic": "Visko Dynamic",
}

LIVE_MODELS = ("helios", "longlive-v2", "sana-streaming", "x2", "visko-orbis-stable", "visko-orbis-dynamic")

__all__ = ["IDENTITIES", "LIVE_MODELS", "MODEL_TITLES"]
