"""Request a session token for one model; support cancellation and a timeout."""

import re
from http import HTTPStatus
import math
import time

import aiohttp

from ..errors import ErrorCode, ConnectorError
from ..serialization import Json, parse_json, mapping_value
from ..config.security import (
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
from ..state.credentials import Credential, SessionToken
from ..config.messages.session import MODEL_AUTHORIZATION

MODEL_NAME = re.compile(MODEL_NAME_PATTERN_TEXT)
TOKEN_TEXT = re.compile(JWT_PATTERN_TEXT)


async def mint_session_token(model: str, credential: Credential, session_seconds: int) -> SessionToken:
    """Authorize one session with a server lifetime cap; never retry a mint.

    Every failure, from the request, the response, or the token, reports the same public authorization error.

    Args:
        model: The model that the token authorizes.
        credential: The API key that authorizes the request.
        session_seconds: The longest session that the token allows, in seconds.

    Returns:
        The session token for the model.

    Raises:
        ConnectorError: When the inputs are out of range or any step of the mint fails.

    """
    if MODEL_NAME.fullmatch(model) is None or not 1 <= session_seconds <= MAX_SESSION_SECONDS:
        raise ConnectorError(ErrorCode.AUTHENTICATION, MODEL_AUTHORIZATION)
    try:
        document = await _request_session(model, credential, session_seconds)
        return _read_session_token(document, session_seconds)
    except (aiohttp.ClientError, TimeoutError, UnicodeError, ConnectorError):
        raise ConnectorError(ErrorCode.AUTHENTICATION, MODEL_AUTHORIZATION) from None


async def _request_session(model: str, credential: Credential, session_seconds: int) -> dict[str, Json]:
    """Request one session token for the model and read the size-limited JSON response.

    Args:
        model: The only model that the token may open.
        credential: The API key sent in the request header.
        session_seconds: The session lifetime cap sent to the server, in seconds.

    Returns:
        The parsed JSON object of the response.

    Raises:
        ConnectorError: When the server refuses the request or the response is too large.

    """
    request_body = {
        'expires_after': session_seconds + SESSION_EXPIRY_BUFFER_SECONDS,
        'authorization_details': [
            {
                'type': 'session',
                'resources': {'models': {'match': [model]}},
                'constraints': {
                    'max_sessions': 1,
                    'max_session_duration_seconds': session_seconds,
                },
            }
        ],
    }
    async with (
        aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=AUTHENTICATION_TIMEOUT_SECONDS),
            trust_env=False,
            cookie_jar=aiohttp.DummyCookieJar(),
        ) as session,
        session.post(
            SESSION_ENDPOINT,
            json=request_body,
            headers={'Reactor-API-Key': credential.value},
            allow_redirects=False,
        ) as response,
    ):
        if response.status != HTTPStatus.OK:
            raise ConnectorError(ErrorCode.AUTHENTICATION, MODEL_AUTHORIZATION)
        response_bytes = bytearray()
        async for chunk in response.content.iter_chunked(AUTHENTICATION_CHUNK_BYTES):
            response_bytes.extend(chunk)
            if len(response_bytes) > MAX_RESPONSE_BYTES:
                raise ConnectorError(ErrorCode.AUTHENTICATION, MODEL_AUTHORIZATION)
    return mapping_value(parse_json(response_bytes.decode(), max_bytes=MAX_RESPONSE_BYTES))


def _read_session_token(document: dict[str, Json], session_seconds: int) -> SessionToken:
    """Accept only a well-formed token whose expiry covers the whole session.

    Args:
        document: The parsed response of the session endpoint.
        session_seconds: The session length that the token expiry has to cover, in seconds.

    Returns:
        The validated session token.

    Raises:
        ConnectorError: When the token is malformed or expires too early.

    """
    token, expires = document.get('jwt'), document.get('expires_at')
    if (
        not isinstance(token, str)
        or len(token) > MAX_SESSION_TOKEN_CHARACTERS
        or TOKEN_TEXT.fullmatch(token) is None
        or not isinstance(expires, (int, float))
        or isinstance(expires, bool)
        or not math.isfinite(expires)
        or expires < time.time() + session_seconds + MIN_EXPIRY_MARGIN_SECONDS
    ):
        raise ConnectorError(ErrorCode.AUTHENTICATION, MODEL_AUTHORIZATION)
    return SessionToken(token)
