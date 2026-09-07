"""Static security values used by the connector."""

MAX_CREDENTIAL_CHARACTERS = 1024

MAX_SESSION_SECONDS = 3600

MAX_SESSION_TOKEN_CHARACTERS = 16_384

SESSION_ENDPOINT = "https://api.reactor.inc/tokens"

MODEL_NAME_PATTERN_TEXT = "[a-z0-9][a-z0-9._-]{0,119}/[a-z0-9][a-z0-9._-]{0,119}"

JWT_PATTERN_TEXT = "[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+"

MAX_RESPONSE_BYTES = 32_768

PRIVATE_HEADERS = {"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"}
