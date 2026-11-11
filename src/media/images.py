"""Convert one native ComfyUI image without silently discarding batch entries."""

import io

from PIL import Image
import numpy as np
from comfy_api.latest import Input

from ..errors import ErrorCode, ConnectorError
from ..config.media.images import RGB_CHANNELS, MAX_IMAGE_DIMENSION, BATCH_IMAGE_DIMENSIONS
from ..config.messages.media import IMAGE_PIXELS, IMAGE_DIMENSIONS, SINGLE_IMAGE_REQUIRED


def encode_png(image: Input.Image) -> bytes:
    """Encode a finite, single red, green, and blue (RGB) image as PNG for the provider upload.

    Args:
        image: The image batch, which must hold one RGB image.

    Returns:
        The PNG bytes.

    Raises:
        ConnectorError: When the batch shape, the dimensions, or the pixel values are invalid.

    """
    if image.ndim != BATCH_IMAGE_DIMENSIONS or image.shape[0] != 1 or image.shape[3] != RGB_CHANNELS:
        raise ConnectorError(ErrorCode.INVALID_INPUT, SINGLE_IMAGE_REQUIRED)
    if image.shape[1] > MAX_IMAGE_DIMENSION or image.shape[2] > MAX_IMAGE_DIMENSION:
        raise ConnectorError(ErrorCode.INVALID_INPUT, IMAGE_DIMENSIONS)
    array = image.detach().cpu().numpy()[0]
    if not np.isfinite(array).all():
        raise ConnectorError(ErrorCode.INVALID_INPUT, IMAGE_PIXELS)
    pixels = np.rint(np.clip(array, 0, 1) * 255).astype(np.uint8)
    with io.BytesIO() as buffer:
        Image.fromarray(pixels).save(buffer, format='PNG')
        return buffer.getvalue()
