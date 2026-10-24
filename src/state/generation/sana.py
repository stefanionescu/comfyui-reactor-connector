"""SANA source and editing request values."""

from dataclasses import dataclass

from .inputs import SourceVideoInputs


@dataclass(frozen=True, slots=True, kw_only=True)
class SanaRequest(SourceVideoInputs):
    """Source selection and edit controls.

    Attributes:
        anchor_interval: Number of chunks between anchors.

    """

    anchor_interval: int
