"""Join observed metadata to reviewed connector identities without guessing support."""

from ..models import MODELS
from .contracts import Snapshot
from ..serialization import Json
from ...config.models.nodes import NODE_MODELS
from ...config.discovery import GUIDE_URL_FORMAT


def model_views(snapshot: Snapshot | None) -> list[dict[str, Json]]:
    """List public models except the excluded HappyOyster family."""
    guides = {guide.slug: guide for guide in snapshot.guides} if snapshot else {}
    prices = {price.name: price for price in snapshot.prices} if snapshot else {}
    associated: set[str] = set()
    models: list[dict[str, Json]] = []
    for name in sorted(set(prices) | set(NODE_MODELS.values())):
        price = prices.get(name)
        definition = MODELS.get(name)
        guide_slug = definition.guide_slug if definition else name
        connect_name = definition.connection_name if definition else None
        guide = guides.get(guide_slug)
        if guide:
            associated.add(guide_slug)
        node_ids: list[Json] = [node_id for node_id, model in NODE_MODELS.items() if model == name]
        model: dict[str, Json] = {
            "key": f"pricing:{price.id}" if price else f"model:{name}",
            "name": name,
            "title": definition.title if definition else guide.title if guide else name,
            "connect_name": connect_name,
            "documentation_url": guide_url(guide_slug) if guide or connect_name else None,
            "credits_per_second": price.credits_per_second if price else None,
            "observed": price.observed if price else False,
            "support": "available" if node_ids else "adapter_required",
            "node_ids": node_ids,
        }
        models.append(model)
    models.extend(
        {
            "key": f"docs:{guide.slug}",
            "name": guide.slug,
            "title": guide.title,
            "connect_name": None,
            "documentation_url": guide_url(guide.slug),
            "credits_per_second": None,
            "observed": guide.observed,
            "support": "adapter_required",
            "node_ids": [],
        }
        for guide in sorted(guides.values(), key=lambda item: item.slug)
        if guide.slug not in associated and not guide.slug.startswith("happy-oyster")
    )
    return models


def guide_url(slug: str) -> str:
    """Build the public overview URL for a model guide name."""
    return GUIDE_URL_FORMAT.format(slug=slug)
