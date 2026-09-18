"""Apply browser input on the same event loop that owns the provider session."""

import time
import asyncio
from ..state.documents import Json
from .controls import ControlLease
from .preview import PreviewFrames
from ..media.output import owned_io
from .commands import CameraCommands
from ..execution.events import SessionEvents
from ..errors import ErrorCode, ConnectorError
from ..execution.transport import Track, Transport
from ..config.nodes import DEFAULT_POINTER_POSITION
from ..config.live import INPUT_POLL_SECONDS, STALE_INPUT_SECONDS, UPLOAD_TIMEOUT_SECONDS, COMMAND_TIMEOUT_SECONDS
from ..config.messages.live import (
    LIVE_PANEL_ENDED,
    LIVE_PREVIEW_ENCODING,
    LIVE_CAPTURE_CANCELLED,
    LIVE_COMMAND_UNFINISHED,
)


class LiveInteraction:
    """Own previews, camera commands, editing actions, and disconnect handling for one session."""

    def __init__(self, lease: ControlLease) -> None:
        """Prepare preview, command, action, and session timing ownership."""
        self.lease = lease
        self.preview = PreviewFrames()
        self.track: Track | None = None
        self.transport: Transport | None = None
        self.worker: asyncio.Task[None] | None = None
        self.action_workers: list[asyncio.Task[None]] = []
        self.active = False
        self.commands: CameraCommands | None = None
        self.preview_frames = 0
        self.accepted_actions = 0
        self.pointer_active = False
        self.controls_started_at: float | None = None
        self.controls_seconds = 0.0
        self.early_video = False

    async def connected(self, transport: Transport, track: Track, events: SessionEvents) -> None:
        """Subscribe to preview frames, watch the owning client, and start the action workers."""
        self.transport = transport
        self.track = track
        track.on_frame(self.preview.receive)
        self.commands = CameraCommands(tuple(self.lease.choices), events)
        self.worker = asyncio.create_task(self._observe(events))
        self.action_workers = [
            asyncio.create_task(self._actions(events, kind)) for kind in ("prompt", "audio_prompt", "pointer")
        ]

    def configured(self, *, video_started: bool) -> None:
        """Enable controls after model setup and record when they became available."""
        self.active = True
        self.controls_started_at = time.monotonic()
        self.early_video = video_started
        self.lease.enable_controls()

    async def _observe(self, events: SessionEvents) -> None:
        """Apply client input, send previews, and stop the session when the client ends."""
        try:
            await self._watch()
        except asyncio.CancelledError:
            raise
        except ConnectorError as error:
            events.on_error(error)
        except (OSError, ValueError):
            events.on_error(ConnectorError(ErrorCode.CAPTURE, LIVE_PREVIEW_ENCODING))

    async def _watch(self) -> None:
        """Watch the client, apply camera input, and update previews until cancellation or disconnection."""
        while True:
            state = self.lease.read()
            if state.end:
                if self.lease.was_ended_by_user():
                    raise ConnectorError(ErrorCode.INTERRUPTED, LIVE_CAPTURE_CANCELLED)
                raise ConnectorError(ErrorCode.TRANSPORT, LIVE_PANEL_ENDED)
            if self.active and self.commands is not None:
                self.commands.submit(state)
            encoded = await owned_io(self.preview.encode)
            if encoded:
                self.lease.frame(encoded)
                self.preview_frames += 1
            await asyncio.sleep(INPUT_POLL_SECONDS)

    async def _actions(self, events: SessionEvents, name: str) -> None:
        """Apply one action type in order and release a stale pointer press."""
        try:
            while True:
                with self.lease.lock:
                    stale = time.monotonic() - self.lease.last_seen > STALE_INPUT_SECONDS
                if name == "pointer" and self.pointer_active and stale:
                    await self._pointer(
                        events,
                        {"x": DEFAULT_POINTER_POSITION, "y": DEFAULT_POINTER_POSITION, "active": False},
                    )
                payload = self.lease.take_action(name) if self.active else None
                if payload is not None:
                    await self._send_action(events, name, payload)
                    self.accepted_actions += 1
                await asyncio.sleep(INPUT_POLL_SECONDS)
        except asyncio.CancelledError:
            raise
        except (ConnectorError, TimeoutError) as error:
            events.on_error(
                error
                if isinstance(error, ConnectorError)
                else ConnectorError(ErrorCode.TIMEOUT, LIVE_COMMAND_UNFINISHED)
            )

    async def _send_action(self, events: SessionEvents, name: str, payload: dict[str, Json]) -> None:
        """Translate a validated live action into this model's command and enforce its reply deadline."""
        if name == "pointer":
            await self._pointer(events, payload)
        elif name == "audio_prompt":
            async with asyncio.timeout(COMMAND_TIMEOUT_SECONDS):
                await events.command_reply("set_audio_prompt", dict(payload))
        else:
            definition = self.lease.definition
            if definition.has_prompt_passthrough:
                payload = {**payload, "passthrough": self.lease.options.is_passthrough_enabled}
            async with asyncio.timeout(COMMAND_TIMEOUT_SECONDS):
                await events.command_reply(definition.prompt_command, dict(payload))

    async def _pointer(self, events: SessionEvents, payload: dict[str, Json]) -> None:
        """Track a possible press before sending it so cleanup covers a missing reply."""
        self.pointer_active = self.pointer_active or payload.get("active") is True
        async with asyncio.timeout(COMMAND_TIMEOUT_SECONDS):
            await events.command_reply("set_pointer", dict(payload))
        self.pointer_active = payload.get("active") is True

    async def stop(self) -> None:
        """Stop the action and camera workers, remove preview listeners, and release an active pointer."""
        for worker in self.action_workers:
            worker.cancel()
        await asyncio.gather(*self.action_workers, return_exceptions=True)
        self.action_workers.clear()
        self.active = False
        if self.controls_started_at is not None:
            self.controls_seconds = time.monotonic() - self.controls_started_at
        self.lease.finish()
        self.preview.close()
        try:
            if self.track is not None:
                self.track.off_frame(self.preview.receive)
                self.track = None
        finally:
            try:
                if self.worker is not None:
                    self.worker.cancel()
                    await asyncio.gather(self.worker, return_exceptions=True)
                    self.worker = None
            finally:
                if self.commands is not None:
                    await self.commands.stop()
        if self.pointer_active and self.transport is not None and self.transport.status == "ready":
            async with asyncio.timeout(UPLOAD_TIMEOUT_SECONDS):
                await self.transport.send_command("set_pointer_active", {"pointer_active": False})
            self.pointer_active = False

    def closed(self, *, is_termination_confirmed: bool, failed: bool) -> None:
        """Publish the final failure and termination status to the owning client."""
        self.lease.close(is_termination_confirmed=is_termination_confirmed, failed=failed)

    def summary(self) -> dict[str, Json]:
        """Report acknowledged controls, not an inference about visible model motion."""
        return {
            "acknowledged_camera_changes": dict(self.commands.accepted) if self.commands else {},
            "maximum_command_reply_seconds": (round(self.commands.maximum_reply_seconds, 3) if self.commands else 0.0),
            "encoded_preview_frames": self.preview_frames,
            "discarded_stale_input_states": self.lease.dropped_states,
            "controls_available_seconds": round(self.controls_seconds, 3),
            "video_arrived_before_controls": self.early_video,
            "acknowledged_live_actions": self.accepted_actions,
        }
