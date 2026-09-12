"""LingBot camera and image-conditioning records."""

from .inputs import VideoInputs
from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class LingBotRequest(VideoInputs):
    """Image conditioning and held camera directions.

    Attributes:
        movement: Selected camera movement.
        look_horizontal: Horizontal camera direction.
        look_vertical: Vertical camera direction.
        rotation_speed_deg: Camera rotation speed in degrees per second.

    """

    movement: str
    look_horizontal: str
    look_vertical: str
    rotation_speed_deg: float


@dataclass(frozen=True, slots=True, kw_only=True)
class LingBotWorldRequest(LingBotRequest):
    """World 2 camera controls with independent lateral movement.

    Attributes:
        lateral: Independent lateral camera movement.

    """

    lateral: str


__all__ = ["LingBotRequest", "LingBotWorldRequest"]
