"""Inspect current public model metadata without using provider credentials."""

import sys
import asyncio
from ..src.discovery.views import model_views
from ..src.discovery.sources import read_public_models


def main() -> None:
    """Read current public prices and guides without changing local state."""
    snapshot = asyncio.run(read_public_models())
    models = model_views(snapshot)
    sys.stdout.write(
        f"Found {len(snapshot.prices)} public price records, {len(snapshot.guides)} guides, "
        f"and {len(models)} model entries. No provider session was opened.\n"
    )


if __name__ == "__main__":
    main()
