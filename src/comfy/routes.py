"""Register local routes with ComfyUI."""

from pathlib import Path

from server import PromptServer
import folder_paths
from comfy.cli_args import args

from ..paths import EXTENSION_ROOT
from ..errors import ErrorCode, ConnectorError
from ..runtime import get_runtime
from ..live.routes import LiveRoutes
from ..settings.routes import ConfigurationRoutes
from ..config.messages.settings import PRIVATE_STATE_LOCATION


def register_configuration() -> None:
    """Reject public state locations before enabling credential writes.

    Raises:
        ConnectorError: When the state directory lies inside a public folder.

    """
    store = get_runtime().configuration
    directory = store.directory.resolve()
    public_roots = (
        folder_paths.base_path,
        folder_paths.get_input_directory(),
        folder_paths.get_output_directory(),
        folder_paths.get_temp_directory(),
        folder_paths.get_user_directory(),
        str(EXTENSION_ROOT),
    )
    if any(directory.is_relative_to(Path(root).resolve()) for root in public_roots):
        raise ConnectorError(
            ErrorCode.CONFIGURATION,
            PRIVATE_STATE_LOCATION,
        )
    ConfigurationRoutes(store, is_multi_user=args.multi_user).register(PromptServer.instance.routes)
    LiveRoutes(get_runtime().browsers, is_multi_user=args.multi_user).register(PromptServer.instance.routes)
