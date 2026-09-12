"""Load Reactor nodes through ComfyUI's extension entry point."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .src.extension import ReactorExtension

# ComfyUI web assets

WEB_DIRECTORY = "./web"


# ComfyUI node registration


async def comfy_entrypoint() -> "ReactorExtension":
    """Import host bindings only when ComfyUI loads the extension."""
    from .src.extension import ReactorExtension  # noqa: PLC0415 -- reason: ComfyUI initializes host imports during extension loading.

    return ReactorExtension()
