"""Load Reactor nodes through ComfyUI's extension entry point."""

WEB_DIRECTORY = "./web"


async def comfy_entrypoint() -> object:
    """Import host bindings only when ComfyUI loads the extension."""
    from .reactor_comfy.extension import ReactorExtension

    return ReactorExtension()
