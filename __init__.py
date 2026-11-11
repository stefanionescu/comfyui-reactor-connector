"""Load Reactor nodes through ComfyUI's extension entry point."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .src.extension import ReactorExtension


WEB_DIRECTORY = './web'


async def comfy_entrypoint() -> 'ReactorExtension':
    """Import host bindings only when ComfyUI loads the extension.

    Returns:
        The extension that registers the Reactor nodes.

    """
    from .src.extension import ReactorExtension  # noqa: PLC0415 # reason: Scripts import the package without ComfyUI.

    return ReactorExtension()
