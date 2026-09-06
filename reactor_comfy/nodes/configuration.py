"""Bind private configuration routes to the actual ComfyUI host."""

from pathlib import Path

import folder_paths
from comfy.cli_args import args
from server import PromptServer

from ..catalog.checker import CatalogChecker
from ..catalog.routes import CatalogRoutes
from ..config_store import load_settings
from ..errors import ConnectorError, ErrorCode
from ..http_routes import ConfigurationRoutes
from ..live.routes import LiveRoutes
from ..runtime import get_runtime


def register_configuration() -> None:
    """Reject public state locations before enabling credential writes."""
    store = get_runtime().configuration
    directory = store.directory.resolve()
    public_roots = (
        folder_paths.base_path,
        folder_paths.get_input_directory(),
        folder_paths.get_output_directory(),
        folder_paths.get_temp_directory(),
        folder_paths.get_user_directory(),
        str(Path(__file__).resolve().parents[2]),
    )
    if any(directory.is_relative_to(Path(root).resolve()) for root in public_roots):
        raise ConnectorError(
            ErrorCode.CONFIGURATION,
            "Keep Reactor's private state outside ComfyUI, its package, and its media folders.",
        )
    ConfigurationRoutes(store, multi_user=args.multi_user).register(PromptServer.instance.routes)
    LiveRoutes(get_runtime().browsers, multi_user=args.multi_user).register(
        PromptServer.instance.routes
    )
    checker = CatalogChecker(get_runtime().catalog, lambda: load_settings(directory))
    PromptServer.instance.app.cleanup_ctx.append(checker.lifecycle)
    CatalogRoutes(get_runtime().catalog, multi_user=args.multi_user, checker=checker).register(
        PromptServer.instance.routes
    )
