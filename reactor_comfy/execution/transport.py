"""Keep the SDK's loosely typed callbacks at one explicit boundary."""

import math
import time
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Protocol, cast

from reactor_sdk import Clip, Reactor

from ..credentials import Credential
from ..errors import ConnectorError, ErrorCode
from .authentication import SessionToken, mint_session_token


class Track(Protocol):
    """The declared media slot used by capture and upload code."""

    @property
    def name(self) -> str: ...

    @property
    def kind(self) -> str | None: ...

    @property
    def direction(self) -> str | None: ...

    def on_frame(self, callback: Callable[..., None]) -> object: ...

    def off_frame(self, callback: Callable[..., None]) -> None: ...

    def push_frame(self, frame: object) -> None: ...


class Transport(Protocol):
    """The released SDK operations consumed by this connector."""

    @property
    def tracks(self) -> Sequence[Track]: ...

    @property
    def status(self) -> str: ...

    def on(self, event: str, callback: Callable[..., None]) -> None: ...

    def off(self, event: str, callback: Callable[..., None]) -> None: ...

    async def connect(self) -> None: ...

    async def disconnect(self) -> None: ...

    def close(self) -> None: ...

    async def request_schema(self) -> object: ...

    async def send_command(self, command: str, data: dict[str, object]) -> object: ...

    async def upload_file(
        self, file: bytes | Path, *, name: str | None = None, mime_type: str | None = None
    ) -> object: ...

    async def publish_track(self, name: str) -> Track: ...

    async def request_recording(self) -> Clip: ...

    async def request_clip(self, duration_seconds: float) -> Clip: ...

    async def save_recording(
        self,
        destination: Path,
        *,
        maximum_bytes: int,
        timeout_seconds: float,
        on_window: Callable[[float, float, float, float], None] | None = None,
    ) -> None: ...


class SessionTransport:
    """Keep the token private and own authentication before creating the SDK client."""

    def __init__(self, model: str, credential: Credential, session_seconds: int) -> None:
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
        return self.client.tracks if self.client else ()

    @property
    def status(self) -> str:
        return self.client.status if self.client else "disconnected"

    def _client(self) -> Transport:
        if self.client is None or self.closed:
            raise ConnectorError(ErrorCode.TRANSPORT, "The Reactor session is not connected.")
        return self.client

    def on(self, event: str, callback: Callable[..., None]) -> None:
        self.handlers.append((event, callback))
        if self.client:
            self.client.on(event, callback)

    def off(self, event: str, callback: Callable[..., None]) -> None:
        if (event, callback) in self.handlers:
            self.handlers.remove((event, callback))
        if self.client:
            self.client.off(event, callback)

    async def connect(self) -> None:
        if self.attempted or self.closed or self.credential is None:
            raise ConnectorError(
                ErrorCode.TRANSPORT, "This Reactor session cannot be connected again."
            )
        self.attempted = True
        self.token = await mint_session_token(self.model, self.credential, self.session_seconds)
        self.credential = None
        # The token already carries the lifetime cap; the SDK must not mint a
        # second token or keep an API key for recording downloads.
        self.client = cast(Transport, Reactor(model_name=self.model, jwt=self.token.value))
        for event, callback in self.handlers:
            self.client.on(event, callback)
        await self.client.connect()

    async def disconnect(self) -> None:
        if self.client:
            await self.client.disconnect()

    def close(self) -> None:
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
        return await self._client().request_schema()

    async def send_command(self, command: str, data: dict[str, object]) -> object:
        return await self._client().send_command(command, data)

    async def upload_file(
        self, file: bytes | Path, *, name: str | None = None, mime_type: str | None = None
    ) -> object:
        if isinstance(file, Path) and file.name == name == "input.mp4" and mime_type == "video/mp4":
            # The SDK's override path reads the entire file on the event loop.
            # Our prepared filename already gives its native path upload the correct MIME type.
            return await self._client().upload_file(file)
        return await self._client().upload_file(file, name=name, mime_type=mime_type)

    async def publish_track(self, name: str) -> Track:
        return await self._client().publish_track(name)

    async def request_recording(self) -> Clip:
        return await self._client().request_recording()

    async def request_clip(self, duration_seconds: float) -> Clip:
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
        from ..media.recording_download import download_recording

        if self.token is None:
            raise ConnectorError(ErrorCode.TRANSPORT, "The recording session is not connected.")
        clip = await self.request_recording()
        markers = (clip.start_marker, clip.end_marker, clip.now_marker)
        if not all(math.isfinite(value) and value >= 0 for value in markers):
            raise ConnectorError(
                ErrorCode.CAPTURE, "The recording returned invalid timing markers."
            )
        if on_window:
            predicted_wait = clip.predicted_ready_at_ms / 1000 - time.time()
            if not math.isfinite(predicted_wait):
                raise ConnectorError(
                    ErrorCode.CAPTURE, "The recording returned invalid readiness timing."
                )
            on_window(*markers, predicted_wait)
        await download_recording(
            clip.playlist_url,
            self.token,
            destination,
            maximum_bytes=maximum_bytes,
            timeout_seconds=timeout_seconds,
        )


def create_transport(model: str, credential: Credential, session_seconds: int) -> Transport:
    """Start network requests only when the session begins its connection timeout."""
    return SessionTransport(model, credential, session_seconds)
