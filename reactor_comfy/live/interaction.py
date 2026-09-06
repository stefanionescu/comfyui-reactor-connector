"""Apply browser input on the same event loop that owns the provider session."""

import asyncio
import time

from ..errors import ConnectorError, ErrorCode
from ..execution.events import SessionEvents
from ..execution.transport import Track, Transport
from ..json_data import Json
from ..media.file_output import owned_io
from .commands import CameraCommands
from .lease import BrowserLease
from .preview import PreviewFrames


class CameraInteraction:
    """Watch a LingBot session and stop recording if the browser disconnects."""

    def __init__(self, lease: BrowserLease) -> None:
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
        self.track = track
        track.on_frame(self.preview.receive)
        self.commands = CameraCommands(tuple(self.lease.choices), events)
        self.worker = asyncio.create_task(self._observe(events))

    def configured(self, *, video_started: bool) -> None:
        self.active = True
        self.controls_started_at = time.monotonic()
        self.early_video = video_started
        self.lease.enable_controls()

    async def _observe(self, events: SessionEvents) -> None:
        try:
            while True:
                state = self.lease.read()
                if state.end:
                    if self.lease.was_ended_by_user():
                        raise ConnectorError(
                            ErrorCode.INTERRUPTED, "The live capture was cancelled."
                        )
                    raise ConnectorError(
                        ErrorCode.TRANSPORT,
                        "The live panel ended or disconnected. The capture has been stopped.",
                    )
                if self.active and self.commands is not None:
                    self.commands.submit(state)
                encoded = await owned_io(self.preview.encode)
                if encoded:
                    self.lease.frame(encoded)
                    self.preview_frames += 1
                await asyncio.sleep(0.05)
        except asyncio.CancelledError:
            raise
        except ConnectorError as error:
            events.on_error(error)
        except (OSError, ValueError):
            events.on_error(
                ConnectorError(
                    ErrorCode.CAPTURE,
                    "The live preview could not be encoded. The session is ending.",
                )
            )

    async def stop(self) -> None:
        self.active = False
        if self.controls_started_at is not None:
            self.controls_seconds = time.monotonic() - self.controls_started_at
        self.lease.finish()
        self.preview.close()
        if self.track is not None:
            self.track.off_frame(self.preview.receive)
            self.track = None
        if self.worker is not None:
            self.worker.cancel()
            await asyncio.gather(self.worker, return_exceptions=True)
            self.worker = None
        if self.commands is not None:
            await self.commands.stop()

    def closed(self, *, termination_confirmed: bool, failed: bool) -> None:
        self.lease.close(termination_confirmed=termination_confirmed, failed=failed)

    def summary(self) -> dict[str, Json]:
        """Report acknowledged controls, not an inference about visible model motion."""
        return {
            "acknowledged_camera_changes": dict(self.commands.accepted) if self.commands else {},
            "maximum_command_reply_seconds": (
                round(self.commands.maximum_reply_seconds, 3) if self.commands else 0.0
            ),
            "encoded_preview_frames": self.preview_frames,
            "discarded_stale_input_states": self.lease.dropped_states,
            "controls_available_seconds": round(self.controls_seconds, 3),
            "video_arrived_before_controls": self.early_video,
        }
