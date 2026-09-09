"""Download an authenticated recording within fixed time and output size limits."""

import re
import math
import aiohttp
import asyncio
from yarl import URL
from pathlib import Path
from http import HTTPStatus
from ..output import FileOutput
from ...language import translate
from ...errors import ErrorCode, ConnectorError
from ...execution.authentication import SessionToken
from ....config.media.recording import MAX_MANIFEST_BYTES, MAX_DOWNLOAD_SECONDS, STORAGE_ERROR_PATTERN
from .manifest import recording_url, coordinator_url, recording_error, RecordingManifest, parse_recording_manifest


def retry_delay(value: str | None) -> float:
    """Limit a provider retry delay to the allowed polling interval."""
    try:
        seconds = float(value) if value else 2.0
    except ValueError:
        seconds = 2.0
    return min(2.0, max(0.2, seconds)) if math.isfinite(seconds) else 2.0


def _headers(url: str, token: SessionToken) -> dict[str, str]:
    """Send the session token only to the verified Reactor coordinator."""
    return {"Authorization": f"Bearer {token.value}"} if coordinator_url(url) else {}


async def _fragment_error(response: aiohttp.ClientResponse, index: int) -> ConnectorError:
    """Keep known storage error codes without saving signed URLs or response bodies."""
    body = await response.content.read(8192)
    match = re.search(STORAGE_ERROR_PATTERN, body)
    code = match.group(1).decode("ascii") if match else ""
    known = {
        "ExpiredToken",
        "InvalidToken",
        "AccessDenied",
        "SignatureDoesNotMatch",
        "AuthorizationQueryParametersError",
        "RequestTimeTooSkewed",
        "RequestExpired",
        "SlowDown",
        "InternalError",
        "NoSuchKey",
    }
    detail = f" Storage code: {code}." if code in known else ""
    return recording_error(f"Recording fragment {index} returned HTTP {response.status}.{detail}")


async def _manifest(session: aiohttp.ClientSession, url: str, token: SessionToken) -> RecordingManifest:
    """Poll for a completed size-limited manifest without following redirects."""
    while True:
        async with session.get(URL(url, encoded=True), headers=_headers(url, token), allow_redirects=False) as response:
            if response.status == HTTPStatus.ACCEPTED:
                delay = retry_delay(response.headers.get("Retry-After"))
            elif response.status == HTTPStatus.OK:
                content = bytearray()
                async for chunk in response.content.iter_chunked(16_384):
                    content.extend(chunk)
                    if len(content) > MAX_MANIFEST_BYTES:
                        raise recording_error()
                return parse_recording_manifest(content.decode(), url)
            else:
                msg = f"Recording manifest request returned HTTP {response.status}."
                raise recording_error(msg)
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
        raise recording_error()
    try:
        async with (
            asyncio.timeout(timeout_seconds),
            aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=20),
                trust_env=False,
                cookie_jar=aiohttp.DummyCookieJar(),
            ) as session,
        ):
            manifest = await _manifest(session, url, token)
            async with FileOutput(destination, maximum_bytes) as output:
                for index, fragment in enumerate((manifest.initialization, *manifest.segments)):
                    # Preserve the exact escaping covered by the storage URL's signature.
                    async with session.get(
                        URL(fragment, encoded=True),
                        headers=_headers(fragment, token),
                        allow_redirects=False,
                    ) as response:
                        if response.status != HTTPStatus.OK:
                            raise await _fragment_error(response, index)
                        received = 0
                        async for chunk in response.content.iter_chunked(65_536):
                            received += len(chunk)
                            await output.write(chunk)
                        if received == 0:
                            raise recording_error()
            return output.written
    except TimeoutError:
        raise ConnectorError(ErrorCode.TIMEOUT, translate("main", "errors.recordingNotReady")) from None
    except (aiohttp.ClientError, UnicodeError, OSError):
        raise recording_error() from None
