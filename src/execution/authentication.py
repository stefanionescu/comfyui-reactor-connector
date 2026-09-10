"""Request a session token for one model; support cancellation and a timeout."""

import re
import math
import time
import aiohttp
from http import HTTPStatus
from ..language import translate
from ..credentials import Credential
from dataclasses import field, dataclass
from ..errors import ErrorCode, ConnectorError
from ..serialization import parse_json, mapping_value
from ...config.security import (
    JWT_PATTERN_TEXT,
    SESSION_ENDPOINT,
    MAX_RESPONSE_BYTES,
    MAX_SESSION_SECONDS,
    MODEL_NAME_PATTERN_TEXT,
    MIN_EXPIRY_MARGIN_SECONDS,
    AUTHENTICATION_CHUNK_BYTES,
    MAX_SESSION_TOKEN_CHARACTERS,
    SESSION_EXPIRY_BUFFER_SECONDS,
    AUTHENTICATION_TIMEOUT_SECONDS,
)


MODEL_NAME = re.compile(MODEL_NAME_PATTERN_TEXT)
TOKEN_TEXT = re.compile(JWT_PATTERN_TEXT)


@dataclass(frozen=True, slots=True, repr=False)
class SessionToken:
    """A private session token and its provider-confirmed expiry time."""

    value: str = field(repr=False)
    expires_at: float

    def __repr__(self) -> str:
        """Hide the token from object representations."""
        return "SessionToken(<redacted>)"

    def __str__(self) -> str:
        """Hide the token from formatted text."""
        return "<redacted>"


def authentication_error() -> ConnectorError:
    """Create the public authorization error without including provider credentials."""
    return ConnectorError(
        ErrorCode.AUTHENTICATION,
        translate("main", "errors.modelAuthorization"),
    )


async def mint_session_token(model: str, credential: Credential, session_seconds: int) -> SessionToken:
    """Authorize one session with a server lifetime cap; never retry a mint."""
    if MODEL_NAME.fullmatch(model) is None or not 1 <= session_seconds <= MAX_SESSION_SECONDS:
        raise authentication_error()
    payload = {
        "expires_after": session_seconds + SESSION_EXPIRY_BUFFER_SECONDS,
        "authorization_details": [
            {
                "type": "session",
                "resources": {"models": {"match": [model]}},
                "constraints": {
                    "max_sessions": 1,
                    "max_session_duration_seconds": session_seconds,
                },
            }
        ],
    }
    try:
        async with (
            aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=AUTHENTICATION_TIMEOUT_SECONDS),
                trust_env=False,
                cookie_jar=aiohttp.DummyCookieJar(),
            ) as session,
            session.post(
                SESSION_ENDPOINT,
                json=payload,
                headers={"Reactor-API-Key": credential.reveal()},
                allow_redirects=False,
            ) as response,
        ):
            if response.status != HTTPStatus.OK:
                raise authentication_error()
            payload = bytearray()
            async for chunk in response.content.iter_chunked(AUTHENTICATION_CHUNK_BYTES):
                payload.extend(chunk)
                if len(payload) > MAX_RESPONSE_BYTES:
                    raise authentication_error()
        document = mapping_value(parse_json(payload.decode(), max_bytes=MAX_RESPONSE_BYTES))
        token, expires = document.get("jwt"), document.get("expires_at")
        if (
            not isinstance(token, str)
            or len(token) > MAX_SESSION_TOKEN_CHARACTERS
            or TOKEN_TEXT.fullmatch(token) is None
            or not isinstance(expires, (int, float))
            or isinstance(expires, bool)
            or not math.isfinite(expires)
            or expires < time.time() + session_seconds + MIN_EXPIRY_MARGIN_SECONDS
        ):
            raise authentication_error()
        return SessionToken(token, float(expires))
    except (aiohttp.ClientError, TimeoutError, UnicodeError, ConnectorError):
        raise authentication_error() from None
