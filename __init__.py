"""Load Reactor nodes through ComfyUI's extension entry point."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .src.extension import ReactorExtension


WEB_DIRECTORY = "./web"


async def comfy_entrypoint() -> "ReactorExtension":
    """Import host bindings only when ComfyUI loads the extension."""
    from .src.extension import ReactorExtension  # noqa: PLC0415 -- reason: ComfyUI initializes host imports during extension loading.

    return ReactorExtension()
