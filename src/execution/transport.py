"""Keep the SDK's loosely typed callbacks at one explicit boundary."""

import math
import time
from pathlib import Path
from ..language import translate
from typing import cast, Protocol
from ..credentials import Credential
from reactor_sdk import Clip, Reactor
from ..errors import ErrorCode, ConnectorError
from collections.abc import Callable, Sequence
from ..media.recording.download import download_recording
from .authentication import SessionToken, mint_session_token


class Track(Protocol):
    """The declared media slot used by capture and upload code."""

    @property
    def name(self) -> str:
        """Return the media slot name declared by the model."""
        raise NotImplementedError

    @property
    def kind(self) -> str | None:
        """Return the media type, or None when the track has no declared type."""
        raise NotImplementedError

    @property
    def direction(self) -> str | None:
        """Return whether the track sends or receives media."""
        raise NotImplementedError

    def on_frame(self, callback: Callable[..., None]) -> object:
        """Register a callback for frames arriving on this track."""
        raise NotImplementedError

    def off_frame(self, callback: Callable[..., None]) -> None:
        """Remove a previously registered frame callback."""
        raise NotImplementedError

    def push_frame(self, frame: object) -> None:
        """Send one frame on an outgoing media track."""
        raise NotImplementedError


class Transport(Protocol):
    """The released SDK operations consumed by this connector."""

    @property
    def tracks(self) -> Sequence[Track]:
        """Return the media tracks declared by the connected model."""
        raise NotImplementedError

    @property
    def status(self) -> str:
        """Return the current connection status reported by the transport."""
        raise NotImplementedError

    def on(self, event: str, callback: Callable[..., None]) -> None:
        """Register a callback for a named transport event."""
        raise NotImplementedError

    def off(self, event: str, callback: Callable[..., None]) -> None:
        """Remove a registered callback from a named transport event."""
        raise NotImplementedError

    async def connect(self) -> None:
        """Open the model connection for this session."""
        raise NotImplementedError

    async def disconnect(self) -> None:
        """Disconnect the model session and await completion."""
        raise NotImplementedError

    def close(self) -> None:
        """Release local transport resources."""
        raise NotImplementedError

    async def request_schema(self) -> object:
        """Request the model's current command and state schema."""
        raise NotImplementedError

    async def send_command(self, command: str, payload: dict[str, object]) -> object:
        """Send a model command and return its correlated reply."""
        raise NotImplementedError

    async def upload_file(self, file: bytes | Path, *, name: str | None = None, mime_type: str | None = None) -> object:
        """Upload bytes or a local file and return the model's file reference."""
        raise NotImplementedError

    async def publish_track(self, name: str) -> Track:
        """Open an outgoing track with the declared model slot name."""
        raise NotImplementedError

    async def request_recording(self) -> Clip:
        """Request the session recording and its timing markers."""
        raise NotImplementedError

    async def request_clip(self, duration_seconds: float) -> Clip:
        """Request a clip of the selected duration from the active session."""
        raise NotImplementedError

    async def save_recording(
        self,
        destination: Path,
        *,
        maximum_bytes: int,
        timeout_seconds: float,
        on_window: Callable[[float, float, float, float], None] | None = None,
    ) -> None:
        """Save the recording within its byte and time limits."""
        raise NotImplementedError


class SessionTransport:
    """Keep the token private and own authentication before creating the SDK client."""

    def __init__(self, model: str, credential: Credential, session_seconds: int) -> None:
        """Retain private authentication inputs until the single connection attempt begins."""
        self.model = model
        self.credential: Credential | None = credential
        self.session_seconds = session_seconds
        self.token: SessionToken | None = None
        self.client: Transport | None = None
        self.handlers: list[tuple[str, Callable[..., None]]] = []
        self.attempted = False
        self.closed = False

    @property
    def tracks(self) -> Sequence[Track]:
        """Return current model tracks, or no tracks before connection."""
        return self.client.tracks if self.client else ()

    @property
    def status(self) -> str:
        """Return the client status, or disconnected before the client exists."""
        return self.client.status if self.client else "disconnected"

    def _client(self) -> Transport:
        """Require an open client before forwarding a transport operation."""
        if self.client is None or self.closed:
            raise ConnectorError(ErrorCode.TRANSPORT, translate("main", "errors.sessionDisconnected"))
        return self.client

    def on(self, event: str, callback: Callable[..., None]) -> None:
        """Retain an event callback and attach it if the client is already present."""
        self.handlers.append((event, callback))
        if self.client:
            self.client.on(event, callback)

    def off(self, event: str, callback: Callable[..., None]) -> None:
        """Remove a retained callback and detach it from the current client."""
        if (event, callback) in self.handlers:
            self.handlers.remove((event, callback))
        if self.client:
            self.client.off(event, callback)

    async def connect(self) -> None:
        """Mint one lifetime-limited token and connect the SDK without retaining the API key."""
        if self.attempted or self.closed or self.credential is None:
            raise ConnectorError(ErrorCode.TRANSPORT, translate("main", "errors.sessionAlreadyConnected"))
        self.attempted = True
        self.token = await mint_session_token(self.model, self.credential, self.session_seconds)
        self.credential = None
        # The token already carries the lifetime cap; the SDK must not mint a
        # second token or keep an API key for recording downloads.
        self.client = cast("Transport", Reactor(model_name=self.model, jwt=self.token.value))
        for event, callback in self.handlers:
            self.client.on(event, callback)
        await self.client.connect()

    async def disconnect(self) -> None:
        """Disconnect the SDK client when one has been created."""
        if self.client:
            await self.client.disconnect()

    def close(self) -> None:
        """Close local resources and clear all retained authentication and callback references."""
        self.closed = True
        try:
            if self.client:
                self.client.close()
        finally:
            self.client = None
            self.token = None
            self.credential = None
            self.handlers.clear()

    async def request_schema(self) -> object:
        """Check connection ownership and request the model schema."""
        return await self._client().request_schema()

    async def send_command(self, command: str, payload: dict[str, object]) -> object:
        """Check connection ownership and send a model command."""
        return await self._client().send_command(command, payload)

    async def upload_file(self, file: bytes | Path, *, name: str | None = None, mime_type: str | None = None) -> object:
        """Upload prepared video by path without forcing the SDK to read it on the event loop."""
        if isinstance(file, Path) and file.name == name == "input.mp4" and mime_type == "video/mp4":
            # The SDK's override path reads the entire file on the event loop.
            # Our prepared filename already gives its native path upload the correct MIME type.
            return await self._client().upload_file(file)
        return await self._client().upload_file(file, name=name, mime_type=mime_type)

    async def publish_track(self, name: str) -> Track:
        """Check connection ownership and open the named outgoing track."""
        return await self._client().publish_track(name)

    async def request_recording(self) -> Clip:
        """Check connection ownership and request the session recording."""
        return await self._client().request_recording()

    async def request_clip(self, duration_seconds: float) -> Clip:
        """Check connection ownership and request a clip of the chosen duration."""
        return await self._client().request_clip(duration_seconds)

    async def save_recording(
        self,
        destination: Path,
        *,
        maximum_bytes: int,
        timeout_seconds: float,
        on_window: Callable[[float, float, float, float], None] | None = None,
    ) -> None:
        """Use the private session token without handing it to a node or workflow."""
        if self.token is None:
            raise ConnectorError(ErrorCode.TRANSPORT, translate("main", "errors.recordingDisconnected"))
        clip = await self.request_recording()
        markers = (clip.start_marker, clip.end_marker, clip.now_marker)
        if not all(math.isfinite(value) and value >= 0 for value in markers):
            raise ConnectorError(ErrorCode.CAPTURE, translate("main", "errors.recordingTiming"))
        if on_window:
            predicted_wait = clip.predicted_ready_at_ms / 1000 - time.time()
            if not math.isfinite(predicted_wait):
                raise ConnectorError(ErrorCode.CAPTURE, translate("main", "errors.recordingReadiness"))
            on_window(*markers, predicted_wait)
        await download_recording(
            clip.playlist_url,
            self.token,
            destination,
            maximum_bytes=maximum_bytes,
            timeout_seconds=timeout_seconds,
        )
