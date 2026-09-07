"""Validate the finite fragmented-MP4 playlist used by Reactor recordings."""

import re
from ...codes import ErrorCode
from dataclasses import dataclass
from ...errors import ConnectorError
from urllib.parse import urljoin, urlsplit
from ....config.media.recording import (
    COORDINATOR,
    MAX_SEGMENTS,
    RECORDING_STORAGE,
    MAX_MANIFEST_BYTES,
    FIRST_URL_CHARACTER,
    INIT_URI_PATTERN_TEXT,
    MAX_RECORDING_URL_CHARACTERS,
)


INIT_URI = re.compile(INIT_URI_PATTERN_TEXT)


def recording_error(reason: str = "Unsupported recording response.") -> ConnectorError:
    """Separate the public recording error from its private diagnostic reason."""
    return ConnectorError(
        ErrorCode.CAPTURE,
        "Reactor returned an unsupported recording. No partial video was saved.",
        diagnostic_detail=reason,
    )


def recording_url(value: str, base: str = COORDINATOR) -> str:
    """Allow only the coordinator and the storage origin verified in live recordings."""
    if len(value) > MAX_RECORDING_URL_CHARACTERS or any(ord(character) < FIRST_URL_CHARACTER for character in value):
        msg = "Recording URL contains whitespace or exceeds its size limit."
        raise recording_error(msg)
    try:
        resolved = urljoin(base, value)
        parts = urlsplit(resolved)
    except ValueError:
        msg = "Recording URL cannot be parsed."
        raise recording_error(msg) from None
    origin = f"{parts.scheme}://{parts.netloc}"
    if (
        origin not in {COORDINATOR, *RECORDING_STORAGE}
        or parts.username is not None
        or parts.password is not None
        or parts.fragment
        or "\\" in resolved
    ):
        msg = f"Recording URL has an unreviewed origin or syntax: {parts.hostname}"
        raise recording_error(msg)
    return resolved


def coordinator_url(value: str) -> bool:
    """Decide whether a validated request may carry the private session token."""
    parts = urlsplit(recording_url(value))
    return f"{parts.scheme}://{parts.netloc}" == COORDINATOR


@dataclass(frozen=True, slots=True)
class RecordingManifest:
    """Validated local filenames for an initialization fragment and recording segments."""

    initialization: str
    segments: tuple[str, ...]


def manifest_lines(text: str) -> list[str]:
    """Require a complete size-limited HLS manifest and reject unsupported media features."""
    if len(text.encode()) > MAX_MANIFEST_BYTES:
        msg = "Recording manifest exceeds its size limit."
        raise recording_error(msg)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines or lines[0] != "#EXTM3U" or lines[-1] != "#EXT-X-ENDLIST":
        msg = "Recording manifest lacks its HLS header or final ENDLIST marker."
        raise recording_error(msg)
    blocked = (
        "#EXT-X-KEY",
        "#EXT-X-SESSION-KEY",
        "#EXT-X-BYTERANGE",
        "#EXT-X-STREAM-INF",
        "#EXT-X-MEDIA:",
        "#EXT-X-DISCONTINUITY",
        "#EXT-X-GAP",
    )
    for line in lines[1:]:
        if line.startswith(blocked):
            tag = next(tag for tag in blocked if line.startswith(tag))
            msg = f"Recording manifest uses an unsupported feature: {tag}"
            raise recording_error(msg)
    return lines[1:]


def parse_recording_manifest(text: str, playlist_url: str) -> RecordingManifest:
    """Validate fragment URLs and reject changing initialization or repeated segments."""
    lines = manifest_lines(text)
    base = recording_url(playlist_url)
    initialization: str | None = None
    segments: list[str] = []
    for line in lines:
        if line.startswith("#EXT-X-MAP"):
            match = INIT_URI.fullmatch(line)
            if match is None or initialization is not None or segments:
                msg = "Recording initialization is malformed, repeated, or out of order."
                raise recording_error(msg)
            initialization = recording_url(match.group(1), base)
        elif not line.startswith("#"):
            if initialization is None or len(segments) >= MAX_SEGMENTS:
                msg = "Recording segment has no initialization or exceeds the count limit."
                raise recording_error(msg)
            segments.append(recording_url(line, base))
    if initialization is None or not segments or len(set(segments)) != len(segments):
        msg = "Recording has missing initialization, no segments, or repeated segments."
        raise recording_error(msg)
    return RecordingManifest(initialization, tuple(segments))
