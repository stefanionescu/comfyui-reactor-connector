"""Run an isolated media worker from this package directory."""

import sys
from typing import TYPE_CHECKING

from src.media import encoding
from src.media.video import worker as video
from src.media.protocol import report_outcome
from src.media.recording import worker as recording

if TYPE_CHECKING:
    from collections.abc import Callable


def main() -> int:
    """Dispatch only the fixed media operations supplied by the connector.

    Returns:
        The exit status of the chosen worker.

    """
    operations: dict[str, Callable[[list[str]], int]] = {
        # The capture worker reports readiness itself, once its output container is open.
        'capture': lambda arguments: report_outcome(
            lambda: encoding.encode(sys.stdin.buffer, encoding.read_settings(arguments)),
            unknown_error_code='encoder_failed',
            known=encoding.EncodingError,
        ),
        'video': video.main,
        'recording': recording.main,
    }
    arguments = sys.argv[1:]
    if not arguments or arguments[0] not in operations:
        sys.stderr.write('Choose a supported media worker.\n')
        return 2
    return operations[arguments[0]](arguments)


if __name__ == '__main__':
    raise SystemExit(main())
