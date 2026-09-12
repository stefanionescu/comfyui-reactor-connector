"""Inspect current public model metadata without using provider credentials."""

import sys
import asyncio
from .nodes.metadata import read_schemas
from ..src.discovery.views import model_views
from ..src.serialization import mapping_value
from ..src.discovery.sources import read_public_models


def main() -> None:
    """Read current public prices and guides without changing local state."""
    snapshot = asyncio.run(read_public_models())
    schemas = mapping_value(read_schemas()["reactor"])
    node_models = {node_id: str(mapping_value(schema)["model"]) for node_id, schema in schemas.items()}
    models = model_views(snapshot, node_models)
    sys.stdout.write(
        f"Found {len(snapshot.prices)} public price records, {len(snapshot.guides)} guides, "
        f"and {len(models)} model entries. No provider session was opened.\n"
    )


if __name__ == "__main__":
    main()
