"""Private error text limits and credential redaction patterns."""

MAX_CODE_CHARACTERS = 256
MAX_MESSAGE_CHARACTERS = 4096
MAX_ERROR_NAME_CHARACTERS = 128
REDACTIONS = (
    ("(?i)\\b(?:rk|sk)_[A-Za-z0-9_-]+", "[credential removed]"),
    ("\\b(?:st|tk|sk)-[^\\s\\\"'<>;,]+", "[credential removed]"),
    ("\\b[A-Za-z0-9_-]{8,}\\.[A-Za-z0-9_-]{8,}\\.[A-Za-z0-9_-]{8,}\\b", "[token removed]"),
    ("https?://[^\\s\\\"'<>]+", "[URL removed]"),
)

__all__ = ["MAX_CODE_CHARACTERS", "MAX_ERROR_NAME_CHARACTERS", "MAX_MESSAGE_CHARACTERS", "REDACTIONS"]
