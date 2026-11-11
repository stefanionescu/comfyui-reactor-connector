"""Create shared runtime ownership when ComfyUI loads the extension."""

from dataclasses import field, dataclass

from .errors import ErrorCode, ConnectorError
from .storage import state_directory
from .live.registry import BrowserRegistry
from .settings.store import ConfigurationStore
from .config.messages.settings import RUNTIME_NOT_READY


@dataclass(frozen=True, slots=True)
class Runtime:
    """State shared by this connector's nodes across executor event loops.

    Attributes:
        browsers: Registry of active browser controls.
        configuration: Private settings and credentials store, under the one private state directory.

    """

    browsers: BrowserRegistry = field(default_factory=BrowserRegistry)
    configuration: ConfigurationStore = field(default_factory=lambda: ConfigurationStore(state_directory()))


_runtime: Runtime | None = None


def initialize_runtime() -> None:
    """Initialize once through the host's extension lifecycle, without network calls."""
    global _runtime  # noqa: PLW0603 # reason: ComfyUI initializes one shared runtime during loading.
    if _runtime is None:
        _runtime = Runtime()


def get_runtime() -> Runtime:
    """Reject execution before the host has loaded the connector.

    Returns:
        The shared runtime.

    Raises:
        ConnectorError: When the runtime is not initialized.

    """
    if _runtime is None:
        raise ConnectorError(ErrorCode.CONFIGURATION, RUNTIME_NOT_READY)
    return _runtime
