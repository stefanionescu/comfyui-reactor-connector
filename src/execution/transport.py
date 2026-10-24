"""Keep the SDK's loosely typed callbacks at one explicit boundary."""

from typing import cast
from pathlib import Path
from collections.abc import Callable

from reactor_sdk import Reactor

from ..errors import ErrorCode, ConnectorError
from .authentication import mint_session_token
from ..state.credentials import Credential, SessionToken
from ..config.messages.media import RECORDING_DISCONNECTED
from ..config.messages.session import SESSION_DISCONNECTED, SESSION_ALREADY_CONNECTED
from ..media.recording.download import download_recording

# The SDK annotates each handler parameter as a bare Callable. These types name the callbacks the connector registers,
# so a cast of the SDK method to one of them keeps the handler typed.
type Callback = Callable[..., None]
type EventRegistration = Callable[[str, Callback], None]
type FrameRegistration = Callable[[Callback], object]


class SessionTransport:
    """Keep the token private and own authentication before creating the SDK client."""

    def __init__(self, model: str, credential: Credential, session_seconds: int) -> None:
        """Retain private authentication inputs until the single connection attempt begins."""
        self.model = model
        self.credential: Credential | None = credential
        self.session_seconds = session_seconds
        self.token: SessionToken | None = None
        self.client: Reactor | None = None
        self.handlers: list[tuple[str, Callback]] = []
        self.attempted = False
        self.closed = False

    def get_client(self) -> Reactor:
        """Return the open SDK client, or stop when the session has no connection."""
        if self.client is None or self.closed:
            raise ConnectorError(ErrorCode.TRANSPORT, SESSION_DISCONNECTED)
        return self.client

    def on(self, event: str, callback: Callback) -> None:
        """Retain an event callback and attach it if the client is already present."""
        self.handlers.append((event, callback))
        if self.client:
            cast('EventRegistration', self.client.on)(event, callback)

    def off(self, event: str, callback: Callback) -> None:
        """Remove a retained callback and detach it from the current client."""
        if (event, callback) in self.handlers:
            self.handlers.remove((event, callback))
        if self.client:
            cast('EventRegistration', self.client.off)(event, callback)

    async def connect(self) -> None:
        """Mint one lifetime-limited token and connect the SDK without retaining the API key."""
        if self.attempted or self.closed or self.credential is None:
            raise ConnectorError(ErrorCode.TRANSPORT, SESSION_ALREADY_CONNECTED)
        self.attempted = True
        self.token = await mint_session_token(self.model, self.credential, self.session_seconds)
        self.credential = None
        # The token already carries the lifetime cap; the SDK must not mint a
        # second token or keep an API key for recording downloads.
        self.client = Reactor(model_name=self.model, jwt=self.token.value)
        for event, callback in self.handlers:
            cast('EventRegistration', self.client.on)(event, callback)
        await self.client.connect()

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

    async def upload_file(self, file: bytes | Path, *, name: str | None = None, mime_type: str | None = None) -> object:
        """Upload prepared video by path without forcing the SDK to read it on the event loop."""
        if isinstance(file, Path) and file.name == name == 'input.mp4' and mime_type == 'video/mp4':
            # The SDK reads the whole file on the event loop when it gets a name and a MIME type.
            # The prepared file name already gives the native path upload the correct MIME type.
            return await self.get_client().upload_file(file)
        return await self.get_client().upload_file(file, name=name, mime_type=mime_type)

    async def save_recording(
        self,
        destination: Path,
        *,
        maximum_bytes: int,
        timeout_seconds: float,
    ) -> None:
        """Use the private session token without handing it to a node or workflow."""
        if self.token is None:
            raise ConnectorError(ErrorCode.TRANSPORT, RECORDING_DISCONNECTED)
        clip = await self.get_client().request_recording()
        await download_recording(
            clip.playlist_url,
            self.token,
            destination,
            maximum_bytes=maximum_bytes,
            timeout_seconds=timeout_seconds,
        )
