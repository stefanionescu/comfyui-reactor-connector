"""Public catalog observations and persisted snapshot values."""

from __future__ import annotations

import json
import hashlib
from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from .documents import Json

FORMAT_VERSION = 1

STORAGE_VERSION = 1


@dataclass(frozen=True, slots=True)
class Price:
    """A public model price and its observation status.

    Attributes:
        id: Provider price identifier.
        name: Provider model name.
        credits_per_second: Published credit rate.
        observed: Whether the current source lists this price.

    """

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


@dataclass(frozen=True, slots=True)
class Guide:
    """A public model guide and its observation status.

    Attributes:
        slug: Provider guide identifier.
        title: Human-readable guide title.
        observed: Whether the current source lists this guide.

    """

    slug: str
    title: str
    observed: bool = True

    def to_json(self) -> dict[str, Json]:
        """Serialize the guide name, title, and observation status."""
        return {"slug": self.slug, "title": self.title, "observed": self.observed}


@dataclass(frozen=True, slots=True)
class Snapshot:
    """A complete observation of public prices and model guides.

    Attributes:
        retrieved_at: Timestamp of the observation.
        credits_per_dollar: Public conversion rate.
        prices: Observed model prices.
        guides: Observed model guides.

    """

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


@dataclass(frozen=True, slots=True)
class CatalogState:
    """The current public snapshot and one optional rollback snapshot.

    Attributes:
        current: Most recently saved observation.
        previous: Prior distinct observation available for restoration.

    """

    current: Snapshot | None = None
    previous: Snapshot | None = None

    @property
    def revision(self) -> str:
        """Identify the cached metadata or the state before the first refresh."""
        return self.current.revision if self.current else hashlib.sha256(b"null").hexdigest()

    def to_json(self) -> dict[str, Json]:
        """Serialize both snapshots in the versioned local storage format."""
        return {
            "version": STORAGE_VERSION,
            "current": self.current.to_json() if self.current else None,
            "previous": self.previous.to_json() if self.previous else None,
        }


__all__ = ["FORMAT_VERSION", "STORAGE_VERSION", "CatalogState", "Guide", "Price", "Snapshot"]
