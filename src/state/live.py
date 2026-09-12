"""Queued browser input records for live sessions."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from .documents import Json


@dataclass(frozen=True, slots=True)
class BrowserInput:
    """Camera directions and their sequence number.

    Attributes:
        sequence: Monotonic browser input number.
        axes: Requested camera directions.
        end: Whether the browser requested a stop.
        received_at: Monotonic arrival time.
        release: Whether held directions should be released.

    """

    sequence: int
    axes: tuple[tuple[str, str], ...]
    end: bool
    received_at: float = 0.0
    release: bool = False


@dataclass(frozen=True, slots=True)
class CameraChange:
    """A requested camera value and its queue arrival time.

    Attributes:
        value: Requested control value.
        queued_at: Monotonic arrival time.

    """

    value: str
    queued_at: float


@dataclass(frozen=True, slots=True)
class BrowserExchange:
    """Validated input for one browser state exchange.

    Attributes:
        sequence: Monotonic browser input number.
        axes: Requested axis values.
        end: Whether the browser requested a stop.
        release: Whether held controls should be released.
        preview_sequence: Last preview received by the browser.

    """

    sequence: int
    axes: dict[str, Json]
    end: bool
    release: bool
    preview_sequence: int


__all__ = ["BrowserExchange", "BrowserInput", "CameraChange"]
