"""Let a browser observer share one owned session without replacing its lifecycle."""

from dataclasses import dataclass
from collections.abc import Callable, Awaitable

from reactor_sdk import Track

from .events import SessionEvents
from .transport import SessionTransport


@dataclass(frozen=True, slots=True)
class SessionInteraction:
    """Session lifecycle callbacks of the live controls of the submitting client.

    Attributes:
        connected: Attaches live controls to the connected transport, output track, and session events.
        configured: Marks the model ready for live actions.
        stop: Stops owned control tasks before session cleanup completes.
        closed: Records whether the session confirmed remote termination, and whether execution failed.

    """

    connected: Callable[[SessionTransport, Track, SessionEvents], Awaitable[None]]
    configured: Callable[[], None]
    stop: Callable[[], Awaitable[None]]
    closed: Callable[[bool, bool], None]
