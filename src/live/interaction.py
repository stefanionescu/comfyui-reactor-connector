"""Apply browser input on the same event loop that owns the provider session."""

import time
from typing import cast
import asyncio

from reactor_sdk import Track

from ..errors import ErrorCode, ConnectorError
from .preview import PreviewFrames
from .commands import CameraCommands
from .controls import ControlLease
from ..config.live import INPUT_POLL_SECONDS, STALE_INPUT_SECONDS, UPLOAD_TIMEOUT_SECONDS, COMMAND_TIMEOUT_SECONDS
from ..config.nodes import DEFAULT_POINTER_POSITION
from ..media.output import owned_io
from ..serialization import Json
from ..execution.events import SessionEvents
from ..execution.transport import SessionTransport, FrameRegistration
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
        self.transport: SessionTransport | None = None
        self.worker: asyncio.Task[None] | None = None
        self.action_workers: list[asyncio.Task[None]] = []
        self.commands: CameraCommands | None = None
        self.pointer_active = False

    async def connected(self, transport: SessionTransport, track: Track, events: SessionEvents) -> None:
        """Subscribe to preview frames, watch the owning client, and start the action workers."""
        self.transport = transport
        self.track = track
        cast('FrameRegistration', track.on_frame)(self.preview.receive)
        self.commands = CameraCommands(tuple(self.lease.choices), events)
        self.worker = asyncio.create_task(self._observe(events))
        self.action_workers = [
            asyncio.create_task(self._actions(events, kind)) for kind in ('prompt', 'audio_prompt', 'pointer')
        ]

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
                with self.lease.lock:
                    is_ended_by_user = self.lease.end_requested
                if is_ended_by_user:
                    raise ConnectorError(ErrorCode.INTERRUPTED, LIVE_CAPTURE_CANCELLED)
                raise ConnectorError(ErrorCode.TRANSPORT, LIVE_PANEL_ENDED)
            # The lease enables controls once the model finishes setup, and disables them when the session finishes.
            with self.lease.lock:
                is_active = self.lease.controls_ready
            if is_active and self.commands is not None:
                self.commands.submit(state)
            encoded = await owned_io(self.preview.encode)
            if encoded:
                self.lease.frame(encoded)
            await asyncio.sleep(INPUT_POLL_SECONDS)

    async def _actions(self, events: SessionEvents, name: str) -> None:
        """Apply one action type in order and release a stale pointer press."""
        try:
            while True:
                with self.lease.lock:
                    stale = time.monotonic() - self.lease.last_seen > STALE_INPUT_SECONDS
                    is_active = self.lease.controls_ready
                if name == 'pointer' and self.pointer_active and stale:
                    await self._pointer(
                        events,
                        {'x': DEFAULT_POINTER_POSITION, 'y': DEFAULT_POINTER_POSITION, 'active': False},
                    )
                payload = self.lease.take_action(name) if is_active else None
                if payload is not None:
                    await self._send_action(events, name, payload)
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
        if name == 'pointer':
            await self._pointer(events, payload)
        elif name == 'audio_prompt':
            async with asyncio.timeout(COMMAND_TIMEOUT_SECONDS):
                await events.command_reply('set_audio_prompt', dict(payload))
        else:
            definition = self.lease.definition
            if definition.has_prompt_passthrough:
                payload = {**payload, 'passthrough': self.lease.options.is_passthrough_enabled}
            async with asyncio.timeout(COMMAND_TIMEOUT_SECONDS):
                await events.command_reply(definition.prompt_command, dict(payload))

    async def _pointer(self, events: SessionEvents, payload: dict[str, Json]) -> None:
        """Track a possible press before sending it so cleanup covers a missing reply."""
        self.pointer_active = self.pointer_active or payload.get('active') is True
        async with asyncio.timeout(COMMAND_TIMEOUT_SECONDS):
            await events.command_reply('set_pointer', dict(payload))
        self.pointer_active = payload.get('active') is True

    async def stop(self) -> None:
        """Stop the action and camera workers, remove preview listeners, and release an active pointer."""
        for worker in self.action_workers:
            worker.cancel()
        await asyncio.gather(*self.action_workers, return_exceptions=True)
        self.action_workers.clear()
        self.lease.finish()
        self.preview.close()
        try:
            if self.track is not None:
                cast('FrameRegistration', self.track.off_frame)(self.preview.receive)
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
        client = self.transport.client if self.transport is not None else None
        if self.pointer_active and client is not None and client.status == 'ready':
            async with asyncio.timeout(UPLOAD_TIMEOUT_SECONDS):
                await client.send_command('set_pointer_active', {'pointer_active': False})
            self.pointer_active = False
