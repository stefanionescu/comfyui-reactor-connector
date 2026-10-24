"""X2 source, reference, and pointer request values."""

from dataclasses import dataclass

from .inputs import SourceVideoInputs


@dataclass(frozen=True, slots=True, kw_only=True)
class X2Request(SourceVideoInputs):
    """Edit controls for a file or live camera source.

    Attributes:
        pointer_x: Normalized horizontal pointer position.
        pointer_y: Normalized vertical pointer position.
        keep_backlog: Whether the provider retains queued source frames.
        pointer_active: Whether pointer control starts active.

    """

    pointer_x: float
    pointer_y: float
    keep_backlog: bool = False
    pointer_active: bool = False
