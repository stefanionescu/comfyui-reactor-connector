"""Load Reactor nodes through ComfyUI's extension entry point."""

# ComfyUI web assets

WEB_DIRECTORY = "./web/dist"


# ComfyUI node registration


async def comfy_entrypoint() -> object:
    """Import host bindings only when ComfyUI loads the extension."""
    from .src.extension import ReactorExtension  # noqa: PLC0415 -- reason: ComfyUI initializes host imports during extension loading.

    return ReactorExtension()
