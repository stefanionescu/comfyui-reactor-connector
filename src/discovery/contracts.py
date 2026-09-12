"""Validate the public metadata stored in a catalog snapshot."""

from __future__ import annotations

import re
import math
from uuid import UUID
from datetime import datetime
from ..language import translate
from typing import TYPE_CHECKING
from ..serialization import mapping_value
from ..errors import ErrorCode, ConnectorError
from ..state.discovery import Price, Guide, Snapshot, FORMAT_VERSION
from ...config.discovery import (
    MAX_MODELS,
    MAX_PRICE_AMOUNT,
    UUID_TEXT_LENGTH,
    SLUG_PATTERN_TEXT,
    FIRST_PRINTABLE_CHARACTER,
    MAX_GUIDE_TITLE_CHARACTERS,
    MAX_RETRIEVAL_TIME_CHARACTERS,
)

if TYPE_CHECKING:
    from ..state.documents import Json


SLUG = re.compile(SLUG_PATTERN_TEXT)


def parse_price(value: dict[str, Json]) -> Price:
    """Validate the price identifier, amount, and observation status."""
    if value.keys() != {"id", "name", "credits_per_second", "observed"}:
        raise invalid()
    identity, amount, observed = value["id"], value["credits_per_second"], value["observed"]
    if not isinstance(identity, str) or len(identity) != UUID_TEXT_LENGTH:
        raise invalid()
    try:
        if str(UUID(identity)) != identity:
            raise invalid()
    except ValueError:
        raise invalid() from None
    if (
        not isinstance(amount, (int, float))
        or isinstance(amount, bool)
        or not 0 <= amount <= MAX_PRICE_AMOUNT
        or not math.isfinite(amount)
        or type(observed) is not bool
    ):
        raise invalid()
    return Price(identity, slug(value["name"]), amount, observed)


def parse_guide(value: dict[str, Json]) -> Guide:
    """Validate the guide name and reject unsafe or oversized titles."""
    if value.keys() != {"slug", "title", "observed"}:
        raise invalid()
    title, observed = value["title"], value["observed"]
    if (
        not isinstance(title, str)
        or not 1 <= len(title) <= MAX_GUIDE_TITLE_CHARACTERS
        or any(ord(character) < FIRST_PRINTABLE_CHARACTER or character in "<>" for character in title)
        or type(observed) is not bool
    ):
        raise invalid()
    return Guide(slug(value["slug"]), title, observed)


def parse_snapshot(value: dict[str, Json]) -> Snapshot:
    """Validate the snapshot format, timestamp, prices, guides, and unique identities."""
    if value.keys() != {"version", "retrieved_at", "credits_per_dollar", "prices", "guides"}:
        raise invalid()
    if type(value["version"]) is not int or value["version"] != FORMAT_VERSION:
        raise invalid()
    retrieved_at, conversion = value["retrieved_at"], value["credits_per_dollar"]
    if not isinstance(retrieved_at, str) or len(retrieved_at) > MAX_RETRIEVAL_TIME_CHARACTERS:
        raise invalid()
    try:
        timestamp = datetime.fromisoformat(retrieved_at)
    except ValueError:
        raise invalid() from None
    if timestamp.tzinfo is None or type(conversion) is not int or not 1 <= conversion <= MAX_PRICE_AMOUNT:
        raise invalid()
    prices = tuple(parse_price(row) for row in rows(value["prices"]))
    guides = tuple(parse_guide(row) for row in rows(value["guides"]))
    if (
        len({price.id for price in prices}) != len(prices)
        or len({price.name for price in prices}) != len(prices)
        or len({guide.slug for guide in guides}) != len(guides)
    ):
        raise invalid()
    # Exclude unsupported HappyOyster entries from refreshed and restored metadata.
    prices = tuple(price for price in prices if not price.name.startswith("happy-oyster"))
    guides = tuple(guide for guide in guides if not guide.slug.startswith("happy-oyster"))
    return Snapshot(retrieved_at, conversion, prices, guides)


def invalid() -> ConnectorError:
    """Create the safe error used for invalid public model metadata."""
    return ConnectorError(ErrorCode.DISCOVERY, translate("main", "errors.modelListFormat"))


def slug(value: Json) -> str:
    """Require a model name that is safe to use in documented identifiers."""
    if not isinstance(value, str) or SLUG.fullmatch(value) is None:
        raise invalid()
    return value


def rows(value: Json) -> list[dict[str, Json]]:
    """Require a nonempty list of model records within the catalog size limit."""
    if not isinstance(value, list) or not 1 <= len(value) <= MAX_MODELS:
        raise invalid()
    return [mapping_value(row) for row in value]


__all__ = ["invalid", "parse_guide", "parse_price", "parse_snapshot", "rows", "slug"]
