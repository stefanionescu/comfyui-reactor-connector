"""Apply browser input on the same event loop that owns the provider session."""

import time
import asyncio
from .lease import BrowserLease
from ..language import translate
from ..state.documents import Json
from .preview import PreviewFrames
from ..media.output import owned_io
from .commands import CameraCommands
from ..execution.events import SessionEvents
from ...config.live import INPUT_POLL_SECONDS
from ..errors import ErrorCode, ConnectorError
from ..execution.transport import Track, Transport


class BrowserInteraction:
    """Own browser previews, optional camera commands, and disconnect handling."""

    def __init__(self, lease: BrowserLease) -> None:
        """Prepare preview, camera-command, and session timing ownership."""
        self.lease = lease
        self.preview = PreviewFrames()
        self.track: Track | None = None
        self.worker: asyncio.Task[None] | None = None
        self.active = False
        self.commands: CameraCommands | None = None
        self.preview_frames = 0
        self.controls_started_at: float | None = None
        self.controls_seconds = 0.0
        self.early_video = False

    async def connected(self, transport: Transport, track: Track, events: SessionEvents) -> None:
        """Subscribe to preview frames and start observing the owning client."""
        del transport
        self.track = track
        track.on_frame(self.preview.receive)
        self.commands = CameraCommands(tuple(self.lease.choices), events)
        self.worker = asyncio.create_task(self._observe(events))

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
            events.on_error(
                ConnectorError(
                    ErrorCode.CAPTURE,
                    translate("main", "errors.livePreviewEncoding"),
                )
            )

    async def _watch(self) -> None:
        """Watch the client, apply camera input, and update previews until cancellation or disconnection."""
        while True:
            state = self.lease.read()
            if state.end:
                if self.lease.was_ended_by_user():
                    raise ConnectorError(ErrorCode.INTERRUPTED, translate("main", "errors.liveCaptureCancelled"))
                raise ConnectorError(
                    ErrorCode.TRANSPORT,
                    translate("main", "errors.livePanelEnded"),
                )
            if self.active and self.commands is not None:
                self.commands.submit(state)
            encoded = await owned_io(self.preview.encode)
            if encoded:
                self.lease.frame(encoded)
                self.preview_frames += 1
            await asyncio.sleep(INPUT_POLL_SECONDS)

    async def stop(self) -> None:
        """Disable controls, remove preview listeners, and await all camera workers."""
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
        }
