"""Create shared runtime ownership when ComfyUI loads the extension."""

from .storage import state_directory
from .live.registry import BrowserRegistry
from .errors import ErrorCode, ConnectorError
from .settings.store import ConfigurationStore
from .config.messages.settings import RUNTIME_NOT_READY


class Runtime:
    """State shared by this connector's nodes across executor event loops.

    Attributes:
        browsers: Registry of active browser controls.
        configuration: Private settings and credentials store.

    """

    __slots__ = ("browsers", "configuration")

    browsers: BrowserRegistry
    configuration: ConfigurationStore

    def __init__(self) -> None:
        """Create process-wide services and place their state under one private directory."""
        self.browsers = BrowserRegistry()
        self.configuration = ConfigurationStore(state_directory())


_runtime: Runtime | None = None


def initialize_runtime() -> None:
    """Initialize once through the host's extension lifecycle, without network calls."""
    global _runtime  # noqa: PLW0603 -- reason: ComfyUI initializes one shared runtime during loading.
    if _runtime is None:
        _runtime = Runtime()


def get_runtime() -> Runtime:
    """Reject execution before the host has loaded the connector."""
    if _runtime is None:
        raise ConnectorError(ErrorCode.CONFIGURATION, RUNTIME_NOT_READY)
    return _runtime
