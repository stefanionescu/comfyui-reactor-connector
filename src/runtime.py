"""Create shared runtime ownership when ComfyUI loads the extension."""

from .state import Runtime
from .errors import ErrorCode, ConnectorError
from .language import translate, read_messages, available_languages


_runtime: Runtime | None = None


def initialize_runtime() -> None:
    """Initialize once through the host's extension lifecycle, without network calls."""
    global _runtime  # noqa: PLW0603 -- reason: ComfyUI initializes one shared runtime during loading.
    for language in available_languages():
        read_messages("nodeDefs", language)
        read_messages("main", language)
    if _runtime is None:
        _runtime = Runtime()


def get_runtime() -> Runtime:
    """Reject execution before the host has loaded the connector."""
    if _runtime is None:
        raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.runtimeNotReady"))
    return _runtime
