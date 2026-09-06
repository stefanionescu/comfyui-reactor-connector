"""Validate the public metadata stored in a catalog snapshot."""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ..errors import ConnectorError, ErrorCode
from ..json_data import Json, object_value

FORMAT_VERSION = 1
MAX_MODELS = 512
SLUG = re.compile(r"[a-z0-9][a-z0-9._-]{0,119}")


def invalid() -> ConnectorError:
    return ConnectorError(
        ErrorCode.CATALOG, "The model catalog has an invalid or unsupported format."
    )


def slug(value: Json) -> str:
    if not isinstance(value, str) or SLUG.fullmatch(value) is None:
        raise invalid()
    return value


def rows(value: Json) -> list[dict[str, Json]]:
    if not isinstance(value, list) or not 1 <= len(value) <= MAX_MODELS:
        raise invalid()
    return [object_value(row) for row in value]


@dataclass(frozen=True, slots=True)
class Price:
    id: str
    name: str
    credits_per_second: int | float
    observed: bool = True

    def to_json(self) -> dict[str, Json]:
        return {
            "id": self.id,
            "name": self.name,
            "credits_per_second": self.credits_per_second,
            "observed": self.observed,
        }

    @classmethod
    def parse(cls, value: dict[str, Json]) -> Price:
        if value.keys() != {"id", "name", "credits_per_second", "observed"}:
            raise invalid()
        identity, amount, observed = value["id"], value["credits_per_second"], value["observed"]
        if not isinstance(identity, str) or len(identity) != 36:
            raise invalid()
        try:
            if str(UUID(identity)) != identity:
                raise invalid()
        except ValueError:
            raise invalid() from None
        if (
            not isinstance(amount, (int, float))
            or isinstance(amount, bool)
            or not 0 <= amount <= 1_000_000_000
            or not math.isfinite(amount)
            or type(observed) is not bool
        ):
            raise invalid()
        return cls(identity, slug(value["name"]), amount, observed)


@dataclass(frozen=True, slots=True)
class Guide:
    slug: str
    title: str
    observed: bool = True

    def to_json(self) -> dict[str, Json]:
        return {"slug": self.slug, "title": self.title, "observed": self.observed}

    @classmethod
    def parse(cls, value: dict[str, Json]) -> Guide:
        if value.keys() != {"slug", "title", "observed"}:
            raise invalid()
        title, observed = value["title"], value["observed"]
        if (
            not isinstance(title, str)
            or not 1 <= len(title) <= 120
            or any(ord(character) < 32 or character in "<>" for character in title)
            or type(observed) is not bool
        ):
            raise invalid()
        return cls(slug(value["slug"]), title, observed)


@dataclass(frozen=True, slots=True)
class Snapshot:
    retrieved_at: str
    credits_per_dollar: int
    prices: tuple[Price, ...]
    guides: tuple[Guide, ...]

    def to_json(self) -> dict[str, Json]:
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
        semantic["guides"] = [
            guide.to_json() for guide in sorted(self.guides, key=lambda g: g.slug)
        ]
        return hashlib.sha256(json.dumps(semantic, sort_keys=True).encode()).hexdigest()

    @classmethod
    def parse(cls, value: dict[str, Json]) -> Snapshot:
        if value.keys() != {"version", "retrieved_at", "credits_per_dollar", "prices", "guides"}:
            raise invalid()
        if type(value["version"]) is not int or value["version"] != FORMAT_VERSION:
            raise invalid()
        retrieved_at, conversion = value["retrieved_at"], value["credits_per_dollar"]
        if not isinstance(retrieved_at, str) or len(retrieved_at) > 40:
            raise invalid()
        try:
            timestamp = datetime.fromisoformat(retrieved_at)
        except ValueError:
            raise invalid() from None
        if timestamp.tzinfo is None or type(conversion) is not int or not 1 <= conversion <= 10**9:
            raise invalid()
        prices = tuple(Price.parse(row) for row in rows(value["prices"]))
        guides = tuple(Guide.parse(row) for row in rows(value["guides"]))
        if (
            len({price.id for price in prices}) != len(prices)
            or len({price.name for price in prices}) != len(prices)
            or len({guide.slug for guide in guides}) != len(guides)
        ):
            raise invalid()
        return cls(retrieved_at, conversion, prices, guides)
