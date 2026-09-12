"""Create shared runtime ownership when ComfyUI loads the extension."""

from .storage import state_directory
from .discovery.store import ModelStore
from .live.registry import BrowserRegistry
from .errors import ErrorCode, ConnectorError
from .settings.store import ConfigurationStore
from .execution.admission import SessionAdmission
from .language import translate, read_messages, available_languages


class Runtime:
    """State shared by this connector's nodes across executor event loops.

    Attributes:
        sessions: Process-wide session admission queue.
        browsers: Registry of active browser controls.
        configuration: Private settings and credentials store.
        discovery: Public model catalog store.

    """

    __slots__ = ("browsers", "configuration", "discovery", "sessions")

    sessions: SessionAdmission
    browsers: BrowserRegistry
    configuration: ConfigurationStore
    discovery: ModelStore

    def __init__(self, node_models: dict[str, str]) -> None:
        """Create process-wide services and place their state under one private directory."""
        self.sessions = SessionAdmission()
        self.browsers = BrowserRegistry()
        self.configuration = ConfigurationStore(state_directory())
        self.discovery = ModelStore(self.configuration.directory / "catalog", node_models)


_runtime: Runtime | None = None


def initialize_runtime(node_models: dict[str, str]) -> None:
    """Initialize once through the host's extension lifecycle, without network calls."""
    global _runtime  # noqa: PLW0603 -- reason: ComfyUI initializes one shared runtime during loading.
    for language in available_languages():
        read_messages("main", language)
    if _runtime is None:
        _runtime = Runtime(node_models)


def get_runtime() -> Runtime:
    """Reject execution before the host has loaded the connector."""
    if _runtime is None:
        raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.runtimeNotReady"))
    return _runtime


__all__ = ["Runtime", "get_runtime", "initialize_runtime"]
