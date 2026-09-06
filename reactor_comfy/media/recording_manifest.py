"""Validate the finite fragmented-MP4 playlist used by Reactor recordings."""

import re
from dataclasses import dataclass
from urllib.parse import urljoin, urlsplit

from ..errors import ConnectorError, ErrorCode

COORDINATOR = "https://api.reactor.inc"
RECORDING_STORAGE = frozenset(
    {
        "https://reactor-uploads-fpcx.s3.us-east-2.amazonaws.com",
        "https://reactor-uploads-zl7p.s3.eu-west-3.amazonaws.com",
    }
)
MAX_MANIFEST_BYTES = 262_144
MAX_SEGMENTS = 512
INIT_URI = re.compile(r'#EXT-X-MAP:URI="([^"\r\n]+)"')


def recording_error(reason: str = "Unsupported recording response.") -> ConnectorError:
    return ConnectorError(
        ErrorCode.CAPTURE,
        "Reactor returned an unsupported recording. No partial video was saved.",
        diagnostic_detail=reason,
    )


def recording_url(value: str, base: str = COORDINATOR) -> str:
    """Allow only the coordinator and the storage origin verified in live recordings."""
    if len(value) > 8192 or any(ord(character) < 33 for character in value):
        raise recording_error("Recording URL contains whitespace or exceeds its size limit.")
    try:
        resolved = urljoin(base, value)
        parts = urlsplit(resolved)
    except ValueError:
        raise recording_error("Recording URL cannot be parsed.") from None
    origin = f"{parts.scheme}://{parts.netloc}"
    if (
        origin not in {COORDINATOR, *RECORDING_STORAGE}
        or parts.username is not None
        or parts.password is not None
        or parts.fragment
        or "\\" in resolved
    ):
        raise recording_error(f"Recording URL has an unreviewed origin or syntax: {parts.hostname}")
    return resolved


def coordinator_url(value: str) -> bool:
    """Decide whether a validated request may carry the private session token."""
    parts = urlsplit(recording_url(value))
    return f"{parts.scheme}://{parts.netloc}" == COORDINATOR


@dataclass(frozen=True, slots=True)
class RecordingManifest:
    initialization: str
    segments: tuple[str, ...]


def parse_recording_manifest(text: str, playlist_url: str) -> RecordingManifest:
    """Reject encryption, byte ranges, alternate tracks, and changing initialization."""
    if len(text.encode()) > MAX_MANIFEST_BYTES:
        raise recording_error("Recording manifest exceeds its size limit.")
    base = recording_url(playlist_url)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines or lines[0] != "#EXTM3U" or lines[-1] != "#EXT-X-ENDLIST":
        raise recording_error("Recording manifest lacks its HLS header or final ENDLIST marker.")
    initialization: str | None = None
    segments: list[str] = []
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
            raise recording_error(f"Recording manifest uses an unsupported feature: {tag}")
        if line.startswith("#EXT-X-MAP"):
            match = INIT_URI.fullmatch(line)
            if match is None or initialization is not None or segments:
                raise recording_error(
                    "Recording initialization is malformed, repeated, or out of order."
                )
            initialization = recording_url(match.group(1), base)
        elif not line.startswith("#"):
            if initialization is None or len(segments) >= MAX_SEGMENTS:
                raise recording_error(
                    "Recording segment has no initialization or exceeds the count limit."
                )
            segments.append(recording_url(line, base))
    if initialization is None or not segments or len(set(segments)) != len(segments):
        raise recording_error(
            "Recording has missing initialization, no segments, or repeated segments."
        )
    return RecordingManifest(initialization, tuple(segments))
