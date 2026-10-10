"""Observe session failures alongside commands and media capture."""

import asyncio
from typing import cast
from .transport import Transport
from ..errors import ErrorCode, ConnectorError
from collections.abc import Callable, Coroutine
from .failures import phase_error, provider_text
from ..config.messages.session import COMMAND_REJECTED, PROVIDER_MESSAGE, CAPTURE_DISCONNECTED


def rejection_message(payload: object) -> str:
    """Add the reason Reactor gave for refusing a command, when it sent one."""
    fields = cast("dict[str, object]", payload) if isinstance(payload, dict) else {}
    reason = fields.get("reason")
    detail = provider_text(reason) if isinstance(reason, str) else ""
    return f"{COMMAND_REJECTED} {PROVIDER_MESSAGE.format(message=detail)}" if detail else COMMAND_REJECTED


class SessionEvents:
    """Own error callbacks and ignore events after teardown starts."""

    def __init__(self, transport: Transport) -> None:
        """Create session signals and failure storage on the current event loop."""
        self.transport = transport
        self.failure: asyncio.Future[ConnectorError] = asyncio.get_running_loop().create_future()
        self.active = True
        self.ready = False
        self.phase = "connect"
        self.generation_complete = asyncio.Event()
        self.state_ready = asyncio.Event()
        self.state: dict[str, object] = {}
        self.state_snapshots: dict[str, dict[str, object]] = {}
        self.state_signals = {kind: asyncio.Event() for kind in ("state", "state_update")}
        self.handlers: list[tuple[str, Callable[..., None]]] = []

    def attach(self) -> None:
        """Register before connection so early errors cannot be missed."""
        for event, callback in (
            ("error", self.on_error),
            ("message", self.on_message),
            ("status_changed", self.on_status),
        ):
            self.transport.on(event, callback)
            self.handlers.append((event, callback))

    def _fail(self, error: ConnectorError) -> None:
        """Preserve the first failure while the session is active."""
        if self.active and not self.failure.done():
            self.failure.set_result(error)

    def on_error(self, error: object) -> None:
        """Stop without retrying a potentially billable operation."""
        if not self.active:
            return
        self._fail(phase_error(error, self.phase))

    def on_message(self, message: object) -> None:
        """Track model state separately from command acknowledgements."""
        if not self.active or not isinstance(message, dict):
            return
        envelope = cast("dict[str, object]", message)
        kind = envelope.get("type")
        payload = envelope.get("data")
        if isinstance(kind, str) and kind in self.state_signals and isinstance(payload, dict):
            self.state = cast("dict[str, object]", payload)
            self.state_ready.set()
            self.state_snapshots[kind] = self.state
            self.state_signals[kind].set()
        if kind == "generation_complete":
            self.generation_complete.set()
        if kind in ("command_error", "action_error"):
            self._fail(ConnectorError(ErrorCode.INVALID_INPUT, rejection_message(envelope.get("data"))))

    def on_status(self, status: object) -> None:
        """Fail if an established connection leaves its ready state."""
        if not self.active:
            return
        if status == "ready":
            self.ready = True
        elif self.ready:
            self._fail(
                ConnectorError(
                    ErrorCode.TRANSPORT,
                    CAPTURE_DISCONNECTED,
                )
            )

    def check(self) -> None:
        """Do not start another operation after a reported failure."""
        if self.failure.done() and not self.failure.cancelled():
            raise self.failure.result()

    async def snapshot(self, kind: str) -> dict[str, object]:
        """Read the model's documented state event without mixing runtime snapshots."""
        await self.state_signals[kind].wait()
        return self.state_snapshots[kind]

    async def command_reply(self, name: str, payload: dict[str, object]) -> object:
        """Return a reply only after checking separately reported model rejection."""
        self.check()
        reply = await self.call(name, self.transport.send_command(name, payload))
        self.on_message(reply)
        self.check()
        return reply

    async def call[T](self, phase: str, operation: Coroutine[object, object, T]) -> T:
        """Identify the failed operation using its caller's fixed phase name."""
        self.phase = phase
        try:
            return await operation
        except Exception as error:  # noqa: BLE001 -- reason: Translate arbitrary SDK failures into connector errors.
            raise phase_error(error, phase) from None

    async def guard[T](self, operation: Coroutine[object, object, T]) -> T:
        """Race one owned operation against the first reported session failure."""
        task = asyncio.create_task(operation)
        try:
            await asyncio.wait({task, self.failure}, return_when=asyncio.FIRST_COMPLETED)
            if self.failure.done():
                raise self.failure.result()
            return await task
        finally:
            if not task.done():
                task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    def close(self) -> None:
        """Disable callbacks before disconnect emits its normal final status."""
        self.active = False
        for event, callback in self.handlers:
            self.transport.off(event, callback)
        self.handlers.clear()
        if not self.failure.done():
            self.failure.cancel()
