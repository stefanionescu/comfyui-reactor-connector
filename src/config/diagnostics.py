"""Limits and redaction patterns for Reactor text shown in errors."""

MAX_MESSAGE_CHARACTERS = 4096
REDACTIONS = (
    ("(?i)\\b(?:rk|sk)_[A-Za-z0-9_-]+", "[credential removed]"),
    ("\\b(?:st|tk|sk)-[^\\s\\\"'<>;,]+", "[credential removed]"),
    ("\\b[A-Za-z0-9_-]{8,}\\.[A-Za-z0-9_-]{8,}\\.[A-Za-z0-9_-]{8,}\\b", "[token removed]"),
    ("https?://[^\\s\\\"'<>]+", "[URL removed]"),
)
