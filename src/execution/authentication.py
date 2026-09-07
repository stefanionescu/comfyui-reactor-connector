"""Request a session token for one model; support cancellation and a timeout."""

import re
import math
import time
import aiohttp
from http import HTTPStatus
from ..codes import ErrorCode
from ..errors import ConnectorError
from ..credentials import Credential
from dataclasses import field, dataclass
from ..serialization import parse_json, mapping_value
from ...config.security import (
    JWT_PATTERN_TEXT,
    SESSION_ENDPOINT,
    MAX_RESPONSE_BYTES,
    MAX_SESSION_SECONDS,
    MODEL_NAME_PATTERN_TEXT,
    MAX_SESSION_TOKEN_CHARACTERS,
)


MODEL_NAME = re.compile(MODEL_NAME_PATTERN_TEXT)
TOKEN_TEXT = re.compile(JWT_PATTERN_TEXT)


def authentication_error() -> ConnectorError:
    """Create the public authorization error without including provider credentials."""
    return ConnectorError(
        ErrorCode.AUTHENTICATION,
        "Reactor could not authorize this model. Check your key and model access before retrying.",
    )


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


async def mint_session_token(model: str, credential: Credential, session_seconds: int) -> SessionToken:
    """Authorize one session with a server lifetime cap; never retry a mint."""
    if MODEL_NAME.fullmatch(model) is None or not 1 <= session_seconds <= MAX_SESSION_SECONDS:
        raise authentication_error()
    payload = {
        "expires_after": session_seconds + 120,
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
                timeout=aiohttp.ClientTimeout(total=25),
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
            async for chunk in response.content.iter_chunked(8192):
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
            or expires < time.time() + session_seconds + 30
        ):
            raise authentication_error()
        return SessionToken(token, float(expires))
    except (aiohttp.ClientError, TimeoutError, UnicodeError, ConnectorError):
        raise authentication_error() from None
