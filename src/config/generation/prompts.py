"""Default prompts, sequence limits, and storyboard transitions."""

DEFAULT_PROMPTS = {
    "shot": "The camera pulls back to reveal the surrounding landscape.",
    "forest": "Sunlight reaches the forest floor as the camera moves forward.",
    "edit": "Change the scene to a soft watercolor painting.",
    "webcam": "Turn the scene into a watercolor painting.",
    "video": "A red ball rolls across a wooden table.",
    "speech": "A person faces the camera and speaks calmly.",
    "fast": "A small stream flows over smooth stones. Water splashes softly and birds call.",
    "continuation": "Follow a stream through a quiet forest. Water splashes softly.",
    "visko": "A small stream flows over smooth stones in a quiet forest.",
}

MAX_PROMPT_CHUNK = 100_000

MAX_PROMPTS = 32

MAX_SEQUENCE_BYTES = 128_000

MAX_SHOT_CHUNK = 100_000

MAX_SHOTS = 32

MAX_STORYBOARD_BYTES = 128_000

OPTIONS_TRANSITION = ["soft", "cut"]

DEFAULT_TRANSITION = "soft"

__all__ = [
    "DEFAULT_PROMPTS",
    "DEFAULT_TRANSITION",
    "MAX_PROMPTS",
    "MAX_PROMPT_CHUNK",
    "MAX_SEQUENCE_BYTES",
    "MAX_SHOTS",
    "MAX_SHOT_CHUNK",
    "MAX_STORYBOARD_BYTES",
    "OPTIONS_TRANSITION",
]
