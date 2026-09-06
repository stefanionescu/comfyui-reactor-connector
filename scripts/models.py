"""Check or refresh public model metadata without using provider credentials."""

import argparse
import asyncio
import json

from reactor_comfy.catalog.sources import fetch_public_catalog
from reactor_comfy.catalog.store import BUNDLED, merge_observations, read_snapshot
from reactor_comfy.catalog.views import model_views


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("check", "refresh", "validate"))
    args = parser.parse_args()
    if args.action in {"check", "refresh"}:
        fresh = asyncio.run(fetch_public_catalog())
        candidate = merge_observations(read_snapshot(BUNDLED), fresh) if BUNDLED.exists() else fresh
        models = model_views(candidate)
        print(f"Observed {len(fresh.prices)} pricing entries and {len(fresh.guides)} model guides.")
        print(
            f"The reconciled list contains {len(models)} entries. No provider session was opened."
        )
        if args.action == "refresh":
            BUNDLED.write_text(json.dumps(candidate.to_json(), indent=2) + "\n")
            print("Updated the public bundled snapshot. Review its changes before release.")
    else:
        candidate = read_snapshot(BUNDLED)
        print(
            f"Validated {len(candidate.prices)} price records and {len(candidate.guides)} guides."
        )


if __name__ == "__main__":
    main()
