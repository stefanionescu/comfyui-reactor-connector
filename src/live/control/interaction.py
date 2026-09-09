"""Apply scene, sound, and pointer changes while a video session is running."""

import asyncio
from .lease import ControlLease
from ...language import translate
from ...serialization import Json
from ..interaction import CameraInteraction
from ...execution.events import SessionEvents
from ...errors import ErrorCode, ConnectorError
from ...execution.transport import Track, Transport
from ....config.live import STALE_INPUT_SECONDS, UPLOAD_TIMEOUT_SECONDS, COMMAND_TIMEOUT_SECONDS


class ControlInteraction(CameraInteraction):
    """Apply live editing actions while retaining the camera session lifecycle."""

    def __init__(self, lease: ControlLease) -> None:
        """Track live command workers and pointer state alongside camera controls."""
        super().__init__(lease)
        self.control_lease = lease
        self.action_workers: list[asyncio.Task[None]] = []
        self.accepted_actions = 0
        self.pointer_active = False
        self.transport: Transport | None = None

    async def connected(self, transport: Transport, track: Track, events: SessionEvents) -> None:
        """Attach camera controls and start independent prompt, sound, and pointer workers."""
        self.transport = transport
        await super().connected(transport, track, events)
        self.action_workers = [
            asyncio.create_task(self._actions(events, kind)) for kind in ("prompt", "audio_prompt", "pointer")
        ]

    async def _actions(self, events: SessionEvents, name: str) -> None:
        """Apply one action type in order and release a stale pointer press."""
        try:
            while True:
                with self.control_lease.lock:
                    stale = self.control_lease.clock() - self.control_lease.last_seen > STALE_INPUT_SECONDS
                if name == "pointer" and self.pointer_active and stale:
                    await self._pointer(events, {"x": 0.5, "y": 0.5, "active": False})
                payload = self.control_lease.take_action(name) if self.active else None
                if payload is not None:
                    await self._send_action(events, name, payload)
                    self.accepted_actions += 1
                await asyncio.sleep(0.05)
        except asyncio.CancelledError:
            raise
        except (ConnectorError, TimeoutError) as error:
            events.on_error(
                error
                if isinstance(error, ConnectorError)
                else ConnectorError(ErrorCode.TIMEOUT, translate("main", "errors.liveCommandUnfinished"))
            )

    async def _send_action(self, events: SessionEvents, name: str, payload: dict[str, Json]) -> None:
        """Translate a validated live action into this model's command and enforce its reply deadline."""
        if name == "pointer":
            await self._pointer(events, payload)
        elif name == "audio_prompt":
            async with asyncio.timeout(COMMAND_TIMEOUT_SECONDS):
                await events.command("set_audio_prompt", dict(payload))
        else:
            if self.control_lease.options.model.startswith("reactor/visko-"):
                payload = {**payload, "passthrough": self.control_lease.options.passthrough}
            async with asyncio.timeout(COMMAND_TIMEOUT_SECONDS):
                await events.command(
                    "set_shot" if self.control_lease.options.model == "reactor/longlive-v2" else "set_prompt",
                    dict(payload),
                )

    async def _pointer(self, events: SessionEvents, payload: dict[str, Json]) -> None:
        # Track a press before sending it so cleanup also covers a missing reply.
        """Track a possible press before sending it so cleanup covers a missing reply."""
        self.pointer_active = self.pointer_active or payload.get("active") is True
        async with asyncio.timeout(COMMAND_TIMEOUT_SECONDS):
            await events.command("set_pointer", dict(payload))
        self.pointer_active = payload.get("active") is True

    async def stop(self) -> None:
        """Stop live workers and camera controls, then release any active pointer."""
        for worker in self.action_workers:
            worker.cancel()
        await asyncio.gather(*self.action_workers, return_exceptions=True)
        self.action_workers.clear()
        await super().stop()
        if self.pointer_active and self.transport is not None and self.transport.status == "ready":
            async with asyncio.timeout(UPLOAD_TIMEOUT_SECONDS):
                await self.transport.send_command("set_pointer_active", {"pointer_active": False})
            self.pointer_active = False

    def summary(self) -> dict[str, Json]:
        """Include acknowledged live-action counts in the public control summary."""
        return {
            **super().summary(),
            "acknowledged_live_actions": self.accepted_actions,
        }
