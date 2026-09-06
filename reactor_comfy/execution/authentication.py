"""Request a session token for one model; support cancellation and a timeout."""

import math
import re
import time
from dataclasses import dataclass, field

import aiohttp

from ..credentials import Credential
from ..errors import ConnectorError, ErrorCode
from ..json_data import object_value, parse_json

TOKEN_URL = "https://api.reactor.inc/tokens"
MODEL_NAME = re.compile(r"[a-z0-9][a-z0-9._-]{0,119}/[a-z0-9][a-z0-9._-]{0,119}")
TOKEN_TEXT = re.compile(r"[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")
MAX_RESPONSE_BYTES = 32_768


def authentication_error() -> ConnectorError:
    return ConnectorError(
        ErrorCode.AUTHENTICATION,
        "Reactor could not authorize this model. Check your key and model access before retrying.",
    )


@dataclass(frozen=True, slots=True, repr=False)
class SessionToken:
    value: str = field(repr=False)
    expires_at: float

    def __repr__(self) -> str:
        return "SessionToken(<redacted>)"

    def __str__(self) -> str:
        return "<redacted>"


async def mint_session_token(
    model: str, credential: Credential, session_seconds: int
) -> SessionToken:
    """Authorize one session with a server lifetime cap; never retry a mint."""
    if MODEL_NAME.fullmatch(model) is None or not 1 <= session_seconds <= 3600:
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
                TOKEN_URL,
                json=payload,
                headers={"Reactor-API-Key": credential.reveal()},
                allow_redirects=False,
            ) as response,
        ):
            if response.status != 200:
                raise authentication_error()
            data = bytearray()
            async for chunk in response.content.iter_chunked(8192):
                data.extend(chunk)
                if len(data) > MAX_RESPONSE_BYTES:
                    raise authentication_error()
        document = object_value(parse_json(data.decode(), max_bytes=MAX_RESPONSE_BYTES))
        token, expires = document.get("jwt"), document.get("expires_at")
        if (
            not isinstance(token, str)
            or len(token) > 16_384
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
