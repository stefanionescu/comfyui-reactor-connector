"""Report the outcome of a media worker on stdout as one JSON line with fixed error codes."""

import sys
import json
from collections.abc import Mapping, Callable


def report_outcome(
    operation: Callable[[], Mapping[str, object]],
    *,
    unknown_error_code: str,
    known: type[Exception] | None = None,
    allowed_codes: frozenset[str] | None = None,
) -> int:
    """Write the result or an error code, never native exception text, and return the exit status."""
    result: Mapping[str, object]
    try:
        result = operation()
    except Exception as error:  # noqa: BLE001 # reason: The worker protocol permits only fixed error codes, never native exception text.
        code = str(error) if known is not None and isinstance(error, known) else unknown_error_code
        if allowed_codes is not None and code not in allowed_codes:
            code = unknown_error_code
        result = {'error': code}
    sys.stdout.write(json.dumps(result) + '\n')
    sys.stdout.flush()
    return int('error' in result)
