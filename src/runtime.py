"""Create shared runtime ownership when ComfyUI loads the extension."""

from .codes import ErrorCode
from .errors import ConnectorError
from .storage import state_directory
from .discovery.store import ModelStore
from dataclasses import field, dataclass
from .live.registry import BrowserRegistry
from .settings.store import ConfigurationStore
from .execution.admission import SessionAdmission


@dataclass(slots=True)
class Runtime:
    """State shared by this connector's nodes across executor event loops."""

    sessions: SessionAdmission = field(default_factory=SessionAdmission)
    browsers: BrowserRegistry = field(default_factory=BrowserRegistry)
    configuration: ConfigurationStore = field(default_factory=lambda: ConfigurationStore(state_directory()))
    discovery: ModelStore = field(init=False)

    def __post_init__(self) -> None:
        """Place model metadata beside the connector's private configuration."""
        self.discovery = ModelStore(self.configuration.directory / "catalog")


_runtime: Runtime | None = None


def initialize_runtime() -> None:
    """Initialize once through the host's extension lifecycle, without network calls."""
    global _runtime  # noqa: PLW0603 -- reason: ComfyUI initializes one shared runtime during loading.
    if _runtime is None:
        _runtime = Runtime()


def get_runtime() -> Runtime:
    """Reject execution before the host has loaded the connector."""
    if _runtime is None:
        raise ConnectorError(ErrorCode.CONFIGURATION, "Reactor has not finished loading. Restart ComfyUI.")
    return _runtime
