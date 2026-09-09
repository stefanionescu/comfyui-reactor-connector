"""Recording download, manifest, and stream limits."""

MAX_DOWNLOAD_SECONDS = 3600

MAX_RECORDING_URL_CHARACTERS = 8192

FIRST_URL_CHARACTER = 33

COORDINATOR = "https://api.reactor.inc"

RECORDING_STORAGE = {
    "https://reactor-uploads-fpcx.s3.us-east-2.amazonaws.com",
    "https://reactor-uploads-zl7p.s3.eu-west-3.amazonaws.com",
}

MAX_MANIFEST_BYTES = 262_144

MAX_SEGMENTS = 512

INIT_URI_PATTERN_TEXT = '#EXT-X-MAP:URI="([^"\\r\\n]+)"'

STORAGE_ERROR_PATTERN = b"<Code>([A-Za-z]{1,64})</Code>"

__all__ = [
    "COORDINATOR",
    "FIRST_URL_CHARACTER",
    "INIT_URI_PATTERN_TEXT",
    "MAX_DOWNLOAD_SECONDS",
    "MAX_MANIFEST_BYTES",
    "MAX_RECORDING_URL_CHARACTERS",
    "MAX_SEGMENTS",
    "RECORDING_STORAGE",
    "STORAGE_ERROR_PATTERN",
]
