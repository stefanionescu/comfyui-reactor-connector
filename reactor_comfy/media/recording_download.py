"""Download an authenticated recording within fixed time and output size limits."""

import asyncio
import math
import re
from pathlib import Path

import aiohttp
from yarl import URL

from ..errors import ConnectorError, ErrorCode
from ..execution.authentication import SessionToken
from .file_output import FileOutput
from .recording_manifest import (
    MAX_MANIFEST_BYTES,
    RecordingManifest,
    coordinator_url,
    parse_recording_manifest,
    recording_error,
    recording_url,
)


def retry_delay(value: str | None) -> float:
    try:
        seconds = float(value) if value else 2.0
    except ValueError:
        seconds = 2.0
    return min(2.0, max(0.2, seconds)) if math.isfinite(seconds) else 2.0


def _headers(url: str, token: SessionToken) -> dict[str, str]:
    return {"Authorization": f"Bearer {token.value}"} if coordinator_url(url) else {}


async def _fragment_error(response: aiohttp.ClientResponse, index: int) -> ConnectorError:
    """Keep known storage error codes without saving signed URLs or response bodies."""
    body = await response.content.read(8192)
    match = re.search(rb"<Code>([A-Za-z]{1,64})</Code>", body)
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


async def _manifest(
    session: aiohttp.ClientSession, url: str, token: SessionToken
) -> RecordingManifest:
    while True:
        async with session.get(
            URL(url, encoded=True), headers=_headers(url, token), allow_redirects=False
        ) as response:
            if response.status == 202:
                delay = retry_delay(response.headers.get("Retry-After"))
            elif response.status == 200:
                data = bytearray()
                async for chunk in response.content.iter_chunked(16_384):
                    data.extend(chunk)
                    if len(data) > MAX_MANIFEST_BYTES:
                        raise recording_error()
                return parse_recording_manifest(data.decode(), url)
            else:
                raise recording_error(
                    f"Recording manifest request returned HTTP {response.status}."
                )
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
    if maximum_bytes < 1 or not 0 < timeout_seconds <= 3600:
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
                        if response.status != 200:
                            raise await _fragment_error(response, index)
                        received = 0
                        async for chunk in response.content.iter_chunked(65_536):
                            received += len(chunk)
                            await output.write(chunk)
                        if received == 0:
                            raise recording_error()
            return output.written
    except TimeoutError:
        raise ConnectorError(
            ErrorCode.TIMEOUT, "The recording was not ready within the capture time limit."
        ) from None
    except (aiohttp.ClientError, UnicodeError, OSError):
        raise recording_error() from None
