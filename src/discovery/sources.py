"""Read only approved public metadata endpoints, without authentication."""

import re
import aiohttp
import asyncio
from http import HTTPStatus
from ..language import translate
from typing import TYPE_CHECKING
from datetime import UTC, datetime
from .navigation import navigation_guides
from ..errors import ErrorCode, ConnectorError
from .contracts import rows, invalid, parse_snapshot
from ..serialization import parse_json, mapping_value
from ..state.discovery import Snapshot, FORMAT_VERSION
from ...config.discovery import (
    INDEX_URL,
    PRICING_URL,
    NAVIGATION_URL,
    MAX_SOURCE_BYTES,
    SOURCE_USER_AGENT,
    SOURCE_CHUNK_BYTES,
    SOURCE_TIMEOUT_SECONDS,
    GUIDE_LINE_PATTERN_TEXT,
)

if TYPE_CHECKING:
    from ..state.documents import Json


GUIDE_LINE = re.compile(
    GUIDE_LINE_PATTERN_TEXT,
    re.MULTILINE,
)


def parse_sources(
    pricing_text: str, index_text: str, retrieved_at: str, navigation_text: str | None = None
) -> Snapshot:
    """Read public model names and rates; discard billing controls and descriptions."""
    pricing = mapping_value(parse_json(pricing_text, max_bytes=MAX_SOURCE_BYTES))
    settings = mapping_value(pricing.get("settings"))
    conversion = settings.get("credits_per_dollar")
    prices: list[Json] = []
    for row in rows(pricing.get("models")):
        rate = mapping_value(row.get("rate"))
        if rate.get("unit") != "credits" or rate.get("denomination") != "second":
            raise invalid()
        prices.append(
            {
                "id": row.get("id"),
                "name": row.get("name"),
                "credits_per_second": rate.get("amount_per_sec"),
                "observed": True,
            }
        )
    if len(index_text.encode()) > MAX_SOURCE_BYTES:
        raise invalid()
    index_entries = GUIDE_LINE.findall(index_text)
    guides: list[Json] = [{"slug": slug, "title": title, "observed": True} for title, slug in index_entries]
    if navigation_text is not None:
        if len(navigation_text.encode()) > MAX_SOURCE_BYTES:
            raise invalid()
        indexed = {slug for _, slug in index_entries}
        guides.extend(guide.to_json() for guide in navigation_guides(navigation_text) if guide.slug not in indexed)
    return parse_snapshot(
        {
            "version": FORMAT_VERSION,
            "retrieved_at": retrieved_at,
            "credits_per_dollar": conversion,
            "prices": prices,
            "guides": guides,
        }
    )


async def _read(session: aiohttp.ClientSession, url: str) -> str:
    """Read a public source within its byte limit and reject redirects."""
    async with session.get(url, allow_redirects=False) as response:
        if response.status != HTTPStatus.OK:
            raise ConnectorError(
                ErrorCode.DISCOVERY,
                translate("main", "errors.modelsHttp", status=response.status),
            )
        content = bytearray()
        async for chunk in response.content.iter_chunked(SOURCE_CHUNK_BYTES):
            content.extend(chunk)
            if len(content) > MAX_SOURCE_BYTES:
                raise invalid()
        return content.decode("utf-8")


async def read_public_models() -> Snapshot:
    """Read and validate public prices and guides without changing the saved list."""
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=SOURCE_TIMEOUT_SECONDS),
            trust_env=False,
            cookie_jar=aiohttp.DummyCookieJar(),
            headers={"User-Agent": SOURCE_USER_AGENT},
        ) as session:
            # Await all reads even when one fails, so no task outlives the session.
            results = await asyncio.gather(
                _read(session, PRICING_URL),
                _read(session, INDEX_URL),
                _read(session, NAVIGATION_URL),
                return_exceptions=True,
            )
        for result in results:
            if isinstance(result, BaseException):
                raise result
        pricing, index, navigation = results
        if not isinstance(pricing, str) or not isinstance(index, str) or not isinstance(navigation, str):
            raise invalid()
        return parse_sources(pricing, index, datetime.now(UTC).isoformat(), navigation)
    except (aiohttp.ClientError, TimeoutError, UnicodeError):
        raise ConnectorError(
            ErrorCode.DISCOVERY,
            translate("main", "errors.modelsUnreadable"),
        ) from None
