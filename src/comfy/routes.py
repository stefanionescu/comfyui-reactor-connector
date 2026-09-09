"""Register local routes and model discovery with ComfyUI."""

import folder_paths
from pathlib import Path
from comfy.cli_args import args
from server import PromptServer
from ..language import translate
from ..runtime import get_runtime
from ..live.routes import LiveRoutes
from ..discovery.routes import ModelRoutes
from ..settings.store import read_settings
from ..discovery.checker import ModelChecker
from ..errors import ErrorCode, ConnectorError
from ..settings.routes import ConfigurationRoutes


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
            translate("main", "errors.privateStateLocation"),
        )
    ConfigurationRoutes(store, multi_user=args.multi_user).register(PromptServer.instance.routes)
    LiveRoutes(get_runtime().browsers, multi_user=args.multi_user).register(PromptServer.instance.routes)
    checker = ModelChecker(get_runtime().discovery, lambda: read_settings(directory))
    PromptServer.instance.app.cleanup_ctx.append(checker.lifecycle)
    ModelRoutes(get_runtime().discovery, multi_user=args.multi_user, checker=checker).register(
        PromptServer.instance.routes
    )
