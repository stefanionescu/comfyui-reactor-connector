"""Join observed metadata to reviewed connector identities without guessing support."""

from ..json_data import Json
from ..node_catalog import NODE_MODELS
from .contracts import Snapshot

# These associations were reviewed against Reactor's model guides on 2026-09-05.
# Catalog entries and runnable node registrations are separate.
IDENTITIES = {
    "fast-h3": ("fast-h3", "reactor/fast-h3"),
    "visko-orbis-stable": ("visko-orbis-stable", "reactor/visko-orbis-stable"),
    "visko-orbis-dynamic": ("visko-orbis-dynamic", "reactor/visko-orbis-dynamic"),
    "helios": ("helios", "reactor/helios"),
    "lingbot": ("lingbot", "reactor/lingbot"),
    "lingbot-world-2": ("lingbot-world-2", "reactor/lingbot-world-2"),
    "longlive-v2": ("longlive-v2", "reactor/longlive-v2"),
    "sana-streaming": ("sana-streaming", "reactor/sana-streaming"),
    "ltx2": ("ltx", "reactor/ltx2"),
    "x2": ("x2", "xmax/x2"),
}

MODEL_TITLES = {
    "fast-h3": "Fast H3",
    "visko-orbis-stable": "Visko Stable",
    "visko-orbis-dynamic": "Visko Dynamic",
}


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
        node_ids: list[Json] = [
            node_id for node_id, model in NODE_MODELS.items() if model == price.name
        ]
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
    for guide in sorted(snapshot.guides, key=lambda item: item.slug):
        if guide.slug not in associated and not guide.slug.startswith("happy-oyster"):
            models.append(
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
            )
    return models


def guide_url(slug: str) -> str:
    return f"https://docs.reactor.inc/model-api-reference/{slug}/overview"
