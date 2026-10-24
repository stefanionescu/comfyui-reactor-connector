"""Video input dimensions, formats, and frame limits."""

from typing import Final

SOURCE_COPY_CHUNK_BYTES = 65_536

# The H.273 transfer-characteristic codes, a standard of the International Telecommunication Union, for the two
# high dynamic range formats: perceptual quantizer and hybrid log-gamma.
HDR_TRANSFER_CODES = (16, 18)

MAX_FRAME_RATE = 120

DEFAULT_FRAME_RATE = 24

COMPONENT_BITS = 8

MIN_FRAME_DIMENSION = 2

MAX_FRAME_DIMENSION = 4096

MIN_SOURCE_FRAMES = 33

MAX_COMPONENT_BITS = 8

MAX_START_SECONDS = 3600

# Final keeps the literal codec name, so PyAV's typing returns a video stream.
ENCODER_NAME: Final = 'libx264'

ENCODER_PIXEL_FORMAT = 'yuv420p'

ENCODER_PRESET = 'veryfast'

ENCODER_CRF = '18'
