"""Join observed metadata to reviewed connector identities without guessing support."""

from .contracts import Snapshot
from ..serialization import Json
from ...config.models import IDENTITIES, NODE_MODELS, MODEL_TITLES

# These associations were reviewed against Reactor's model guides on 2026-09-05.
# Catalog entries and runnable node registrations are separate.


def model_views(snapshot: Snapshot) -> list[dict[str, Json]]:
    """List public models except the excluded HappyOyster family."""
    guides = {guide.slug: guide for guide in snapshot.guides}
    associated: set[str] = set()
    models: list[dict[str, Json]] = []
    for price in sorted(snapshot.prices, key=lambda item: item.name):
        if price.name.startswith("happy-oyster"):
            continue
        guide_slug, connect_name = IDENTITIES.get(price.name, (price.name, None))
        guide = guides.get(guide_slug)
        if guide:
            associated.add(guide_slug)
        node_ids: list[Json] = [node_id for node_id, model in NODE_MODELS.items() if model == price.name]
        model: dict[str, Json] = {
            "key": f"pricing:{price.id}",
            "name": price.name,
            "title": MODEL_TITLES.get(price.name, guide.title if guide else price.name),
            "connect_name": connect_name,
            "documentation_url": guide_url(guide_slug) if guide else None,
            "credits_per_second": price.credits_per_second,
            "observed": price.observed,
            "support": "available" if node_ids else "adapter_required",
            "node_ids": node_ids,
            "availability": "unknown",
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
            "availability": "unknown",
        }
        for guide in sorted(snapshot.guides, key=lambda item: item.slug)
        if guide.slug not in associated and not guide.slug.startswith("happy-oyster")
    )
    return models


def guide_url(slug: str) -> str:
    """Build the public overview URL for a model guide name."""
    return f"https://docs.reactor.inc/model-api-reference/{slug}/overview"
