"""Check or refresh public model metadata without using provider credentials."""

import sys
import json
import asyncio
import argparse
from ..src.discovery.views import model_views
from ..src.discovery.sources import read_public_models
from ..src.discovery.store import BUNDLED, read_snapshot, merge_observations


def main() -> None:
    """Validate or refresh public model metadata without opening a provider session."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("check", "refresh", "validate"))
    args = parser.parse_args()
    if args.action in {"check", "refresh"}:
        fresh = asyncio.run(read_public_models())
        candidate = merge_observations(read_snapshot(BUNDLED), fresh) if BUNDLED.exists() else fresh
        models = model_views(candidate)
        sys.stdout.write(
            str(f"Observed {len(fresh.prices)} pricing entries and {len(fresh.guides)} model guides.") + "\n"
        )
        sys.stdout.write(
            str(f"The reconciled list contains {len(models)} entries. No provider session was opened.") + "\n"
        )
        if args.action == "refresh":
            BUNDLED.write_text(json.dumps(candidate.to_json(), indent=2) + "\n")
            sys.stdout.write("Updated the public bundled snapshot. Review its changes before release." + "\n")
    else:
        candidate = read_snapshot(BUNDLED)
        sys.stdout.write(
            str(f"Validated {len(candidate.prices)} price records and {len(candidate.guides)} guides.") + "\n"
        )


if __name__ == "__main__":
    main()
