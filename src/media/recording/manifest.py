"""Validate the finite fragmented-MP4 playlist used by Reactor recordings."""

import re
from urllib.parse import urljoin, urlsplit

from ...errors import ErrorCode, ConnectorError
from ...state.recording import RecordingManifest
from ...config.messages.media import RECORDING_UNSUPPORTED
from ...config.media.recording import (
    COORDINATOR,
    MAX_SEGMENTS,
    RECORDING_STORAGE,
    MAX_MANIFEST_BYTES,
    FIRST_URL_CHARACTER,
    INIT_URI_PATTERN_TEXT,
    MAX_RECORDING_URL_CHARACTERS,
)

INIT_URI = re.compile(INIT_URI_PATTERN_TEXT)


def recording_url(value: str, base: str = COORDINATOR) -> str:
    """Allow only the coordinator and the storage origin verified in live recordings.

    Args:
        value: The address to check, absolute or relative.
        base: The address that resolves a relative value.

    Returns:
        The resolved address.

    Raises:
        ConnectorError: When the address is too long, malformed, or from another origin.

    """
    if len(value) > MAX_RECORDING_URL_CHARACTERS or any(ord(character) < FIRST_URL_CHARACTER for character in value):
        message = 'Recording URL contains whitespace or exceeds its size limit.'
        raise ConnectorError(ErrorCode.CAPTURE, f'{RECORDING_UNSUPPORTED} {message}')
    try:
        resolved = urljoin(base, value)
        parts = urlsplit(resolved)
    except ValueError:
        message = 'Recording URL cannot be parsed.'
        raise ConnectorError(ErrorCode.CAPTURE, f'{RECORDING_UNSUPPORTED} {message}') from None
    origin = f'{parts.scheme}://{parts.netloc}'
    if (
        origin not in {COORDINATOR, *RECORDING_STORAGE}
        or parts.username is not None
        or parts.password is not None
        or parts.fragment
        or '\\' in resolved
    ):
        message = f'Recording URL has an unreviewed origin or syntax: {parts.hostname}'
        raise ConnectorError(ErrorCode.CAPTURE, f'{RECORDING_UNSUPPORTED} {message}')
    return resolved


def manifest_lines(text: str) -> list[str]:
    """Require a complete size-limited HTTP Live Streaming (HLS) manifest and reject unsupported media features.

    Args:
        text: The manifest text.

    Returns:
        The nonempty lines after the header.

    Raises:
        ConnectorError: When the manifest is too large, incomplete, or uses an unsupported feature.

    """
    if len(text.encode()) > MAX_MANIFEST_BYTES:
        message = 'Recording manifest exceeds its size limit.'
        raise ConnectorError(ErrorCode.CAPTURE, f'{RECORDING_UNSUPPORTED} {message}')
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines or lines[0] != '#EXTM3U' or lines[-1] != '#EXT-X-ENDLIST':
        message = 'Recording manifest lacks its HLS header or final ENDLIST marker.'
        raise ConnectorError(ErrorCode.CAPTURE, f'{RECORDING_UNSUPPORTED} {message}')
    blocked = (
        '#EXT-X-KEY',
        '#EXT-X-SESSION-KEY',
        '#EXT-X-BYTERANGE',
        '#EXT-X-STREAM-INF',
        '#EXT-X-MEDIA:',
        '#EXT-X-DISCONTINUITY',
        '#EXT-X-GAP',
    )
    for line in lines[1:]:
        if line.startswith(blocked):
            tag = next(tag for tag in blocked if line.startswith(tag))
            message = f'Recording manifest uses an unsupported feature: {tag}'
            raise ConnectorError(ErrorCode.CAPTURE, f'{RECORDING_UNSUPPORTED} {message}')
    return lines[1:]


def parse_recording_manifest(text: str, playlist_url: str) -> RecordingManifest:
    """Validate fragment URLs and reject changing initialization or repeated segments.

    Args:
        text: The manifest text to parse.
        playlist_url: The manifest address, which resolves relative fragment addresses.

    Returns:
        The initialization address and the segment addresses.

    Raises:
        ConnectorError: When the initialization or the segments are missing, repeated, or out of order.

    """
    lines = manifest_lines(text)
    base = recording_url(playlist_url)
    initialization: str | None = None
    segments: list[str] = []
    for line in lines:
        if line.startswith('#EXT-X-MAP'):
            match = INIT_URI.fullmatch(line)
            if match is None or initialization is not None or segments:
                message = 'Recording initialization is malformed, repeated, or out of order.'
                raise ConnectorError(ErrorCode.CAPTURE, f'{RECORDING_UNSUPPORTED} {message}')
            initialization = recording_url(match.group(1), base)
        elif not line.startswith('#'):
            if initialization is None or len(segments) >= MAX_SEGMENTS:
                message = 'Recording segment has no initialization or exceeds the count limit.'
                raise ConnectorError(ErrorCode.CAPTURE, f'{RECORDING_UNSUPPORTED} {message}')
            segments.append(recording_url(line, base))
    if initialization is None or not segments or len(set(segments)) != len(segments):
        message = 'Recording has missing initialization, no segments, or repeated segments.'
        raise ConnectorError(ErrorCode.CAPTURE, f'{RECORDING_UNSUPPORTED} {message}')
    return RecordingManifest(initialization, tuple(segments))
