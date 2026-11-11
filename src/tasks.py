"""Wait for owned tasks that must settle even when the caller gets cancelled."""

import asyncio


async def wait_shielded[T](task: asyncio.Task[T]) -> bool:
    """Wait until the task settles despite cancellation, and report whether cancellation arrived.

    Args:
        task: The task to wait for.

    Returns:
        Whether a cancellation arrived during the wait.

    """
    cancelled = False
    while not task.done():
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError:
            cancelled = True
        except Exception:  # noqa: BLE001 # reason: The caller reads the settled task's failure after resolving cancellation.
            break
    return cancelled
