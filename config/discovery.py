"""Public model sources, snapshot limits, and refresh validation."""

UUID_TEXT_LENGTH = 36

MAX_PRICE_AMOUNT = 1_000_000_000

MAX_GUIDE_TITLE_CHARACTERS = 120

FIRST_PRINTABLE_CHARACTER = 32

MAX_RETRIEVAL_TIME_CHARACTERS = 40

FORMAT_VERSION = 1

STORAGE_VERSION = 1

MAX_MODELS = 512

SLUG_PATTERN_TEXT = "[a-z0-9][a-z0-9._-]{0,119}"

MAX_MODEL_GUIDES = 512

GUIDE_PATH_PATTERN_TEXT = (
    "(?:https://docs\\.reactor\\.inc)?/model-api-reference/([a-z0-9][a-z0-9._-]{0,119})/overview(?:\\.md)?/?"
)

PRICING_URL = "https://api.reactor.inc/pricing"

INDEX_URL = "https://docs.reactor.inc/llms.txt"

NAVIGATION_URL = "https://docs.reactor.inc/model-api-reference/overview"

GUIDE_URL_FORMAT = "https://docs.reactor.inc/model-api-reference/{slug}/overview"

MAX_SOURCE_BYTES = 1_048_576

SOURCE_CHUNK_BYTES = 16_384

SOURCE_TIMEOUT_SECONDS = 20

SOURCE_USER_AGENT = "reactor-inc/catalog"

GUIDE_LINE_PATTERN_TEXT = "^- \\[([^\\]\\n]+)\\]\\(https://docs\\.reactor\\.inc/model-api-reference/([a-z0-9._-]+)/overview(?:\\.md)?\\)(?::.*)?$"

CHECK_TIMEOUT_SECONDS = 25

CHECK_POLL_SECONDS = 60

MAX_STORED_METADATA_BYTES = 2_097_152
MAX_ADDED_MODELS = 20
SOURCE_RETENTION_DIVISOR = 2

__all__ = [
    "CHECK_POLL_SECONDS",
    "CHECK_TIMEOUT_SECONDS",
    "FIRST_PRINTABLE_CHARACTER",
    "FORMAT_VERSION",
    "GUIDE_LINE_PATTERN_TEXT",
    "GUIDE_PATH_PATTERN_TEXT",
    "GUIDE_URL_FORMAT",
    "INDEX_URL",
    "MAX_ADDED_MODELS",
    "MAX_GUIDE_TITLE_CHARACTERS",
    "MAX_MODELS",
    "MAX_MODEL_GUIDES",
    "MAX_PRICE_AMOUNT",
    "MAX_RETRIEVAL_TIME_CHARACTERS",
    "MAX_SOURCE_BYTES",
    "MAX_STORED_METADATA_BYTES",
    "NAVIGATION_URL",
    "PRICING_URL",
    "SLUG_PATTERN_TEXT",
    "SOURCE_CHUNK_BYTES",
    "SOURCE_RETENTION_DIVISOR",
    "SOURCE_TIMEOUT_SECONDS",
    "SOURCE_USER_AGENT",
    "STORAGE_VERSION",
    "UUID_TEXT_LENGTH",
]
