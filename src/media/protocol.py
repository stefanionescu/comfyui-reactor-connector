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
    """Write the result or an error code, never native exception text, and return the exit status.

    Args:
        operation: The work whose result is reported.
        unknown_error_code: The code to report for an unexpected failure.
        known: The exception class whose text is a fixed code, or None.
        allowed_codes: The codes that may be reported, or None to allow any.

    Returns:
        1 when an error is reported, or 0 otherwise.

    """
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


def report_ready_outcome(
    operation: Callable[[], Mapping[str, object]],
    *,
    unknown_error_code: str,
    known: type[Exception] | None = None,
    allowed_codes: frozenset[str] | None = None,
) -> int:
    """Announce that the worker started, then report the outcome of its work.

    Args:
        operation: The work to run after the readiness line.
        unknown_error_code: The code that stands for an unexpected failure.
        known: The exception class whose text is a fixed code, or None.
        allowed_codes: The codes that may leave the worker, or None to allow any.

    Returns:
        The exit status that report_outcome gives.

    """
    sys.stdout.write(json.dumps({'ready': True}) + '\n')
    sys.stdout.flush()
    return report_outcome(operation, unknown_error_code=unknown_error_code, known=known, allowed_codes=allowed_codes)
