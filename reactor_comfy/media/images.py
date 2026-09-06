"""Convert one native ComfyUI image without silently discarding batch entries."""

import io

import numpy as np
from comfy_api.latest import Input
from PIL import Image

from ..errors import ConnectorError, ErrorCode


def image_png(image: Input.Image) -> bytes:
    """Encode a finite, single RGB image as PNG for the provider upload."""
    if image.ndim != 4 or image.shape[0] != 1 or image.shape[3] != 3:
        raise ConnectorError(ErrorCode.INVALID_INPUT, "Connect exactly one RGB image, not a batch.")
    if image.shape[1] > 8192 or image.shape[2] > 8192:
        raise ConnectorError(
            ErrorCode.INVALID_INPUT, "Use an image no larger than 8192 pixels per side."
        )
    array = image.detach().cpu().numpy()[0]
    if not np.isfinite(array).all():
        raise ConnectorError(ErrorCode.INVALID_INPUT, "The image contains non-finite pixel values.")
    pixels = np.rint(np.clip(array, 0, 1) * 255).astype(np.uint8)
    with io.BytesIO() as buffer:
        Image.fromarray(pixels).save(buffer, format="PNG")
        return buffer.getvalue()
