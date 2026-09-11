"""Validate the public metadata stored in a catalog snapshot."""

from __future__ import annotations

import re
import json
import math
import hashlib
from uuid import UUID
from datetime import datetime
from ..language import translate
from dataclasses import dataclass
from ..errors import ErrorCode, ConnectorError
from ..serialization import Json, mapping_value
from ...config.discovery import (
    MAX_MODELS,
    FORMAT_VERSION,
    MAX_PRICE_AMOUNT,
    UUID_TEXT_LENGTH,
    SLUG_PATTERN_TEXT,
    FIRST_PRINTABLE_CHARACTER,
    MAX_GUIDE_TITLE_CHARACTERS,
    MAX_RETRIEVAL_TIME_CHARACTERS,
)


SLUG = re.compile(SLUG_PATTERN_TEXT)


@dataclass(frozen=True, slots=True)
class Price:
    """A public model price and whether the latest source still lists it."""

    id: str
    name: str
    credits_per_second: int | float
    observed: bool = True

    def to_json(self) -> dict[str, Json]:
        """Serialize the model price and its observation status."""
        return {
            "id": self.id,
            "name": self.name,
            "credits_per_second": self.credits_per_second,
            "observed": self.observed,
        }

    @classmethod
    def parse(cls, value: dict[str, Json]) -> Price:
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
        return cls(identity, slug(value["name"]), amount, observed)


@dataclass(frozen=True, slots=True)
class Guide:
    """A public model guide and whether it appeared in the latest source."""

    slug: str
    title: str
    observed: bool = True

    def to_json(self) -> dict[str, Json]:
        """Serialize the guide name, title, and observation status."""
        return {"slug": self.slug, "title": self.title, "observed": self.observed}

    @classmethod
    def parse(cls, value: dict[str, Json]) -> Guide:
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
        return cls(slug(value["slug"]), title, observed)


@dataclass(frozen=True, slots=True)
class Snapshot:
    """A complete observation of public prices and model guides."""

    retrieved_at: str
    credits_per_dollar: int
    prices: tuple[Price, ...]
    guides: tuple[Guide, ...]

    def to_json(self) -> dict[str, Json]:
        """Serialize the versioned public model snapshot."""
        return {
            "version": FORMAT_VERSION,
            "retrieved_at": self.retrieved_at,
            "credits_per_dollar": self.credits_per_dollar,
            "prices": [price.to_json() for price in self.prices],
            "guides": [guide.to_json() for guide in self.guides],
        }

    @property
    def revision(self) -> str:
        """Ignore retrieval time and source ordering when comparing model metadata."""
        semantic = self.to_json()
        del semantic["retrieved_at"]
        semantic["prices"] = [price.to_json() for price in sorted(self.prices, key=lambda p: p.id)]
        semantic["guides"] = [guide.to_json() for guide in sorted(self.guides, key=lambda g: g.slug)]
        return hashlib.sha256(json.dumps(semantic, sort_keys=True).encode()).hexdigest()

    @classmethod
    def parse(cls, value: dict[str, Json]) -> Snapshot:
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
        prices = tuple(Price.parse(row) for row in rows(value["prices"]))
        guides = tuple(Guide.parse(row) for row in rows(value["guides"]))
        if (
            len({price.id for price in prices}) != len(prices)
            or len({price.name for price in prices}) != len(prices)
            or len({guide.slug for guide in guides}) != len(guides)
        ):
            raise invalid()
        # Exclude unsupported HappyOyster entries from refreshed and restored metadata.
        prices = tuple(price for price in prices if not price.name.startswith("happy-oyster"))
        guides = tuple(guide for guide in guides if not guide.slug.startswith("happy-oyster"))
        return cls(retrieved_at, conversion, prices, guides)


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
