"""Convert one native ComfyUI image without silently discarding batch entries."""

import io
import numpy as np
from PIL import Image
from ..codes import ErrorCode
from comfy_api.latest import Input
from ..errors import ConnectorError
from ...config.media.images import RGB_CHANNELS, MAX_IMAGE_DIMENSION, BATCH_IMAGE_DIMENSIONS


def image_png(image: Input.Image) -> bytes:
    """Encode a finite, single RGB image as PNG for the provider upload."""
    if image.ndim != BATCH_IMAGE_DIMENSIONS or image.shape[0] != 1 or image.shape[3] != RGB_CHANNELS:
        raise ConnectorError(ErrorCode.INVALID_INPUT, "Connect exactly one RGB image, not a batch.")
    if image.shape[1] > MAX_IMAGE_DIMENSION or image.shape[2] > MAX_IMAGE_DIMENSION:
        raise ConnectorError(ErrorCode.INVALID_INPUT, "Use an image no larger than 8192 pixels per side.")
    array = image.detach().cpu().numpy()[0]
    if not np.isfinite(array).all():
        raise ConnectorError(ErrorCode.INVALID_INPUT, "The image contains non-finite pixel values.")
    pixels = np.rint(np.clip(array, 0, 1) * 255).astype(np.uint8)
    with io.BytesIO() as buffer:
        Image.fromarray(pixels).save(buffer, format="PNG")
        return buffer.getvalue()
