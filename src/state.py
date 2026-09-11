"""Shared connector state created when ComfyUI loads the extension."""

from .storage import state_directory
from .discovery.store import ModelStore
from .live.registry import BrowserRegistry
from .settings.store import ConfigurationStore
from .execution.admission import SessionAdmission


class Runtime:
    """State shared by this connector's nodes across executor event loops."""

    __slots__ = ("browsers", "configuration", "discovery", "sessions")

    sessions: SessionAdmission
    browsers: BrowserRegistry
    configuration: ConfigurationStore
    discovery: ModelStore

    def __init__(self) -> None:
        """Create process-wide services and place their state under one private directory."""
        self.sessions = SessionAdmission()
        self.browsers = BrowserRegistry()
        self.configuration = ConfigurationStore(state_directory())
        self.discovery = ModelStore(self.configuration.directory / "catalog")


__all__ = ["Runtime"]
