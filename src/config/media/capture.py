"""Video frame dimensions, queue limits, and encoding parameters."""

from ..messages.media import (
    NO_FRAMES,
    TRUNCATED,
    DIMENSIONS,
    FILE_LIMIT,
    FRAME_SIZE,
    SOURCE_HDR,
    TIMESTAMPS,
    SOURCE_RATE,
    SOURCE_VIDEO,
    SOURCE_FRAMES,
    ENCODER_FAILED,
    SOURCE_STREAMS,
    RECORDING_AUDIO,
    RECORDING_VIDEO,
    RECORDING_MEMORY,
    SOURCE_FRAME_LIMIT,
    SOURCE_TIME_MISSING,
    RECORDING_UNREADABLE,
)

MIN_FRAME_DIMENSION = 2

MAX_FRAME_DIMENSION = 8192

FRAME_HEADER_FORMAT = "<IIq"

ENCODER_ERRORS = {
    "dimensions": DIMENSIONS,
    "frame_size": FRAME_SIZE,
    "timestamps": TIMESTAMPS,
    "file_limit": FILE_LIMIT,
    "no_frames": NO_FRAMES,
    "truncated": TRUNCATED,
    "encoder_failed": ENCODER_FAILED,
    "source_frames": SOURCE_FRAMES,
    "source_video": SOURCE_VIDEO,
    "source_streams": SOURCE_STREAMS,
    "source_hdr": SOURCE_HDR,
    "source_rate": SOURCE_RATE,
    "source_time_missing": SOURCE_TIME_MISSING,
    "source_frame_limit": SOURCE_FRAME_LIMIT,
    "recording_video": RECORDING_VIDEO,
    "recording_audio": RECORDING_AUDIO,
    "recording_memory": RECORDING_MEMORY,
    "recording_details": RECORDING_UNREADABLE,
}

MAX_DURATION_MICROSECONDS = 3_601_000_000

MAX_QUEUED_FRAMES = 16
