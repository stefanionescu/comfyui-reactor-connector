"""Run an isolated media worker from this package directory."""

import sys
from src.media import encoding
from src.media.video import worker as video
from src.media.metadata import worker as metadata
from src.media.recording import worker as recording


def main() -> int:
    """Dispatch only the fixed media operations supplied by the connector."""
    operations = {
        "capture": encoding.main,
        "video": video.main,
        "metadata": metadata.main,
        "recording": recording.main,
    }
    arguments = sys.argv[1:]
    if not arguments or arguments[0] not in operations:
        sys.stderr.write("Choose a supported media worker.\n")
        return 2
    return operations[arguments[0]](arguments)


if __name__ == "__main__":
    raise SystemExit(main())
