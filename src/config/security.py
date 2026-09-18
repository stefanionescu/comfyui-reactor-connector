"""Limits and prefixes of the local API and the Reactor authentication endpoint."""

SETTINGS_PREFIX = "/reactor-inc/v1"

MODELS_PREFIX = "/reactor-inc/v1/catalog"

MAX_JSON_BYTES = 1_048_576

MAX_JSON_DEPTH = 16

MAX_CREDENTIAL_CHARACTERS = 1024

MAX_SESSION_SECONDS = 3600

MAX_SESSION_TOKEN_CHARACTERS = 16_384

SESSION_ENDPOINT = "https://api.reactor.inc/tokens"

MODEL_NAME_PATTERN_TEXT = "[a-z0-9][a-z0-9._-]{0,119}/[a-z0-9][a-z0-9._-]{0,119}"

JWT_PATTERN_TEXT = "[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+"

MAX_RESPONSE_BYTES = 32_768

AUTHENTICATION_CHUNK_BYTES = 8_192

AUTHENTICATION_TIMEOUT_SECONDS = 25

SESSION_EXPIRY_BUFFER_SECONDS = 120

MIN_EXPIRY_MARGIN_SECONDS = 30

PRIVATE_HEADERS = {"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"}
