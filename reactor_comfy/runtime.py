"""Create shared runtime ownership when ComfyUI loads the extension."""

from dataclasses import dataclass, field

from .catalog.store import CatalogStore
from .config_store import ConfigurationStore
from .errors import ConnectorError, ErrorCode
from .execution.admission import SessionAdmission
from .live.lease import BrowserRegistry
from .storage import state_directory


@dataclass(slots=True)
class Runtime:
    """State shared by this connector's nodes across executor event loops."""

    sessions: SessionAdmission = field(default_factory=SessionAdmission)
    browsers: BrowserRegistry = field(default_factory=BrowserRegistry)
    configuration: ConfigurationStore = field(
        default_factory=lambda: ConfigurationStore(state_directory())
    )
    catalog: CatalogStore = field(init=False)

    def __post_init__(self) -> None:
        self.catalog = CatalogStore(self.configuration.directory / "catalog")


_runtime: Runtime | None = None


def initialize_runtime() -> None:
    """Initialize once through the host's extension lifecycle, without network calls."""
    global _runtime
    if _runtime is None:
        _runtime = Runtime()


def get_runtime() -> Runtime:
    """Reject execution before the host has loaded the connector."""
    if _runtime is None:
        raise ConnectorError(
            ErrorCode.CONFIGURATION, "Reactor has not finished loading. Restart ComfyUI."
        )
    return _runtime
