"""Static media capture values used by the connector."""

MIN_FRAME_DIMENSION = 2

MAX_FRAME_DIMENSION = 8192

FRAME_HEADER_FORMAT = "<IIq"

ENCODER_ERRORS = {
    "dimensions": "Video dimensions changed during capture.",
    "frame_size": "Video frames must have even dimensions within the capture limit.",
    "timestamps": "Video timestamps stopped increasing.",
    "file_limit": "The captured video exceeds its file limit.",
    "no_frames": "No video frames were captured.",
    "truncated": "The encoder received an incomplete frame.",
    "encoder_failed": "Video encoding failed. Check free disk space and the host's media support.",
    "source_frames": "Use a source video with at least 33 frames within the input time limit.",
    "source_video": "Use a readable local SDR video with increasing timestamps.",
    "source_streams": "Use a video file with exactly one video track.",
    "source_hdr": "The video uses HDR color. Convert it to SDR before using it.",
    "source_rate": "The video needs a frame rate from 1 to 120 frames per second.",
    "source_time_missing": "The video is missing frame timestamps.",
    "source_frame_limit": "The video exceeds 120 frames per second within the selected duration.",
    "recording_video": "The recording has unsupported video or invalid timestamps.",
    "recording_audio": "The recording needs one mono or stereo audio track with valid timestamps.",
    "recording_memory": "The recording exceeds the configured media memory limit.",
    "recording_details": "The saved video's details could not be read.",
}

MAX_DURATION_MICROSECONDS = 3_601_000_000

MAX_QUEUED_FRAMES = 16
