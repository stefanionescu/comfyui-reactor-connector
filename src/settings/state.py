"""Private settings and credential snapshots used for execution."""

from .settings import Settings
from ..credentials import Credential
from dataclasses import field, dataclass


@dataclass(frozen=True, slots=True)
class ExecutionConfiguration:
    """One private settings and credential snapshot for an admitted operation."""

    settings: Settings
    credential: Credential = field(repr=False)
    generation: str


__all__ = ["ExecutionConfiguration"]
