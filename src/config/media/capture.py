"""Video frame dimensions, queue limits, and encoding parameters."""

MIN_FRAME_DIMENSION = 2

MAX_FRAME_DIMENSION = 8192

FRAME_HEADER_FORMAT = "<IIq"

ENCODER_ERRORS = {
    "dimensions": "mediaErrors.dimensions",
    "frame_size": "mediaErrors.frame_size",
    "timestamps": "mediaErrors.timestamps",
    "file_limit": "mediaErrors.file_limit",
    "no_frames": "mediaErrors.no_frames",
    "truncated": "mediaErrors.truncated",
    "encoder_failed": "mediaErrors.encoder_failed",
    "source_frames": "mediaErrors.source_frames",
    "source_video": "mediaErrors.source_video",
    "source_streams": "mediaErrors.source_streams",
    "source_hdr": "mediaErrors.source_hdr",
    "source_rate": "mediaErrors.source_rate",
    "source_time_missing": "mediaErrors.source_time_missing",
    "source_frame_limit": "mediaErrors.source_frame_limit",
    "recording_video": "mediaErrors.recording_video",
    "recording_audio": "mediaErrors.recording_audio",
    "recording_memory": "mediaErrors.recording_memory",
    "recording_details": "mediaErrors.recording_details",
}

MAX_DURATION_MICROSECONDS = 3_601_000_000

MAX_QUEUED_FRAMES = 16

__all__ = [
    "ENCODER_ERRORS",
    "FRAME_HEADER_FORMAT",
    "MAX_DURATION_MICROSECONDS",
    "MAX_FRAME_DIMENSION",
    "MAX_QUEUED_FRAMES",
    "MIN_FRAME_DIMENSION",
]
