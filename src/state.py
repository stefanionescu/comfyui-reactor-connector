"""Shared connector state created when ComfyUI loads the extension."""

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


__all__ = ["Runtime"]
