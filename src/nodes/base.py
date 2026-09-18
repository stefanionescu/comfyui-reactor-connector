"""Share the cache key and the run-number input across the video nodes."""

from typing import ClassVar
from comfy_api.latest import io
from collections.abc import Callable, Awaitable
from ..comfy.execution import operation_fingerprint


class VideoNode(io.ComfyNode):
    """Own the cache key and the run-number input every video node shares.

    Attributes:
        contract: Operation revision included in the cache key.
        generate: Typed entry point that receives every saved input except the run number.

    """

    contract: ClassVar[str]
    generate: ClassVar[Callable[..., Awaitable[io.NodeOutput]]]

    @classmethod
    async def fingerprint_inputs(cls, **_inputs: object) -> str:
        """Include the operation revision and private configuration token in the cache key."""
        return await operation_fingerprint(cls.contract)

    @classmethod
    async def execute(cls, **inputs: object) -> io.NodeOutput:  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI awaits an async execute.
        """Drop the run number, which ComfyUI uses to invalidate its cache, and generate."""
        inputs.pop("variation", None)
        return await cls.generate(**inputs)


__all__ = ["VideoNode"]
