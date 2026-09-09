"""Read only approved public metadata endpoints, without authentication."""

import re
import aiohttp
import asyncio
from http import HTTPStatus
from ..language import translate
from datetime import UTC, datetime
from .navigation import navigation_guides
from ..errors import ErrorCode, ConnectorError
from ..serialization import Json, parse_json, mapping_value
from .contracts import rows, Guide, Price, invalid, Snapshot
from ...config.discovery import INDEX_URL, PRICING_URL, NAVIGATION_URL, MAX_SOURCE_BYTES, GUIDE_LINE_PATTERN_TEXT


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
        price = Price.parse(
            {
                "id": row.get("id"),
                "name": row.get("name"),
                "credits_per_second": rate.get("amount_per_sec"),
                "observed": True,
            }
        )
        prices.append(price.to_json())
    if len(index_text.encode()) > MAX_SOURCE_BYTES:
        raise invalid()
    guides: list[Json] = [
        Guide.parse({"slug": slug, "title": title, "observed": True}).to_json()
        for title, slug in GUIDE_LINE.findall(index_text)
    ]
    if navigation_text is not None:
        if len(navigation_text.encode()) > MAX_SOURCE_BYTES:
            raise invalid()
        indexed = {slug for _, slug in GUIDE_LINE.findall(index_text)}
        guides.extend(guide.to_json() for guide in navigation_guides(navigation_text) if guide.slug not in indexed)
    return Snapshot.parse(
        {
            "version": 1,
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
        async for chunk in response.content.iter_chunked(16_384):
            content.extend(chunk)
            if len(content) > MAX_SOURCE_BYTES:
                raise invalid()
        return content.decode("utf-8")


async def read_public_models() -> Snapshot:
    """Reconcile pricing, the text index, and navigation before replacing the cache."""
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=20),
            trust_env=False,
            cookie_jar=aiohttp.DummyCookieJar(),
            headers={"User-Agent": "reactor-inc/catalog"},
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
