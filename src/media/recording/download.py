"""Download an authenticated recording within fixed time and output size limits."""

import re
from http import HTTPStatus
import math
import asyncio
from pathlib import Path
from urllib.parse import urlsplit

from yarl import URL
import aiohttp

from ..output import FileOutput
from ...errors import ErrorCode, ConnectorError
from .manifest import recording_url, parse_recording_manifest
from ...state.recording import RecordingManifest
from ...state.credentials import SessionToken
from ...config.messages.media import RECORDING_NOT_READY, RECORDING_UNSUPPORTED
from ...config.media.recording import (
    COORDINATOR,
    MAX_RETRY_SECONDS,
    MEDIA_CHUNK_BYTES,
    MIN_RETRY_SECONDS,
    MAX_MANIFEST_BYTES,
    ERROR_RESPONSE_BYTES,
    MANIFEST_CHUNK_BYTES,
    MAX_DOWNLOAD_SECONDS,
    DEFAULT_RETRY_SECONDS,
    STORAGE_ERROR_PATTERN,
    REQUEST_TIMEOUT_SECONDS,
)


def retry_delay(value: str | None) -> float:
    """Limit a provider retry delay to the allowed polling interval."""
    try:
        seconds = float(value) if value else DEFAULT_RETRY_SECONDS
    except ValueError:
        seconds = DEFAULT_RETRY_SECONDS
    return min(MAX_RETRY_SECONDS, max(MIN_RETRY_SECONDS, seconds)) if math.isfinite(seconds) else DEFAULT_RETRY_SECONDS


def _request(url: str, token: SessionToken) -> tuple[URL, dict[str, str]]:
    """Keep the exact escaping that the storage URL signs, and send the session token only to the coordinator."""
    parts = urlsplit(recording_url(url))
    is_coordinator = f'{parts.scheme}://{parts.netloc}' == COORDINATOR
    headers = {'Authorization': f'Bearer {token.value}'} if is_coordinator else {}
    return URL(url, encoded=True), headers


async def _fragment_error(response: aiohttp.ClientResponse, index: int) -> ConnectorError:
    """Keep known storage error codes without saving signed URLs or response bodies."""
    body = await response.content.read(ERROR_RESPONSE_BYTES)
    match = re.search(STORAGE_ERROR_PATTERN, body)
    code = match.group(1).decode('ascii') if match else ''
    known = {
        'ExpiredToken',
        'InvalidToken',
        'AccessDenied',
        'SignatureDoesNotMatch',
        'AuthorizationQueryParametersError',
        'RequestTimeTooSkewed',
        'RequestExpired',
        'SlowDown',
        'InternalError',
        'NoSuchKey',
    }
    detail = f' Storage code: {code}.' if code in known else ''
    return ConnectorError(
        ErrorCode.CAPTURE,
        f'{RECORDING_UNSUPPORTED} Recording fragment {index} returned HTTP {response.status}.{detail}',
    )


async def _manifest(session: aiohttp.ClientSession, url: str, token: SessionToken) -> RecordingManifest:
    """Poll for a completed size-limited manifest without following redirects."""
    while True:
        target, headers = _request(url, token)
        async with session.get(target, headers=headers, allow_redirects=False) as response:
            if response.status == HTTPStatus.ACCEPTED:
                delay = retry_delay(response.headers.get('Retry-After'))
            elif response.status == HTTPStatus.OK:
                content = bytearray()
                async for chunk in response.content.iter_chunked(MANIFEST_CHUNK_BYTES):
                    content.extend(chunk)
                    if len(content) > MAX_MANIFEST_BYTES:
                        raise ConnectorError(ErrorCode.CAPTURE, RECORDING_UNSUPPORTED)
                return parse_recording_manifest(content.decode(), url)
            else:
                msg = f'Recording manifest request returned HTTP {response.status}.'
                raise ConnectorError(ErrorCode.CAPTURE, f'{RECORDING_UNSUPPORTED} {msg}')
        await asyncio.sleep(delay)


async def download_recording(
    playlist_url: str,
    token: SessionToken,
    destination: Path,
    *,
    maximum_bytes: int,
    timeout_seconds: float,
) -> int:
    """Download recording headers and media in order; discard incomplete files."""
    url = recording_url(playlist_url)
    if maximum_bytes < 1 or not 0 < timeout_seconds <= MAX_DOWNLOAD_SECONDS:
        raise ConnectorError(ErrorCode.CAPTURE, RECORDING_UNSUPPORTED)
    try:
        async with (
            asyncio.timeout(timeout_seconds),
            aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SECONDS),
                trust_env=False,
                cookie_jar=aiohttp.DummyCookieJar(),
            ) as session,
        ):
            manifest = await _manifest(session, url, token)
            async with FileOutput(destination, maximum_bytes) as output:
                for index, fragment in enumerate((manifest.initialization, *manifest.segments)):
                    target, headers = _request(fragment, token)
                    async with session.get(target, headers=headers, allow_redirects=False) as response:
                        if response.status != HTTPStatus.OK:
                            raise await _fragment_error(response, index)
                        received = 0
                        async for chunk in response.content.iter_chunked(MEDIA_CHUNK_BYTES):
                            received += len(chunk)
                            await output.write(chunk)
                        if received == 0:
                            raise ConnectorError(ErrorCode.CAPTURE, RECORDING_UNSUPPORTED)
            return output.written
    except TimeoutError:
        raise ConnectorError(ErrorCode.TIMEOUT, RECORDING_NOT_READY) from None
    except (aiohttp.ClientError, UnicodeError, OSError):
        raise ConnectorError(ErrorCode.CAPTURE, RECORDING_UNSUPPORTED) from None
