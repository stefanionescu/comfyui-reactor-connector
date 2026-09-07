"""Static discovery values used by the connector."""

UUID_TEXT_LENGTH = 36

MAX_PRICE_AMOUNT = 1_000_000_000

MAX_GUIDE_TITLE_CHARACTERS = 120

FIRST_PRINTABLE_CHARACTER = 32

MAX_RETRIEVAL_TIME_CHARACTERS = 40

FORMAT_VERSION = 1

MAX_MODELS = 512

SLUG_PATTERN_TEXT = "[a-z0-9][a-z0-9._-]{0,119}"

MAX_MODEL_GUIDES = 512

GUIDE_PATH_PATTERN_TEXT = (
    "(?:https://docs\\.reactor\\.inc)?/model-api-reference/([a-z0-9][a-z0-9._-]{0,119})/overview(?:\\.md)?/?"
)

PRICING_URL = "https://api.reactor.inc/pricing"

INDEX_URL = "https://docs.reactor.inc/llms.txt"

NAVIGATION_URL = "https://docs.reactor.inc/model-api-reference/overview"

MAX_SOURCE_BYTES = 1_048_576

GUIDE_LINE_PATTERN_TEXT = "^- \\[([^\\]\\n]+)\\]\\(https://docs\\.reactor\\.inc/model-api-reference/([a-z0-9._-]+)/overview(?:\\.md)?\\)(?::.*)?$"

CHECK_TIMEOUT_SECONDS = 25
