"""Share the cache key and the run-number input across the video nodes."""

from typing import ClassVar, override
import asyncio
from collections.abc import Callable, Awaitable

from comfy_api.latest import io

from ..runtime import get_runtime


class VideoNode(io.ComfyNode):
    """Own the cache key and the run-number input every video node shares.

    Attributes:
        generate: Typed entry point that receives every saved input except the run number.

    """

    generate: ClassVar[Callable[..., Awaitable[io.NodeOutput]]]

    @classmethod
    @override
    async def fingerprint_inputs(cls, **_inputs: object) -> str:
        """Add the settings and key token to the cache key, so a new key or limit runs the node again.

        Args:
            **_inputs: Unused saved inputs of the node.

        Returns:
            The token that changes with the settings and the key.

        """
        configuration = await asyncio.to_thread(get_runtime().configuration.read_execution_configuration)
        return configuration.generation

    @classmethod
    @override
    async def execute(cls, **inputs: object) -> io.NodeOutput:  # pyright: ignore[reportIncompatibleMethodOverride] # reason: ComfyUI awaits an async execute.
        """Drop the run number, which ComfyUI uses to invalidate its cache, and generate.

        Args:
            **inputs: The saved inputs of the node, with the run number.

        Returns:
            The output of the node.

        """
        inputs.pop('variation', None)
        return await cls.generate(**inputs)
