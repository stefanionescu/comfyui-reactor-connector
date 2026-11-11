"""Serve one owner-checked exchange without exposing a general model-command proxy."""

import asyncio
from functools import partial
from dataclasses import field, dataclass

from aiohttp import web

from ..errors import ErrorCode, ConnectorError
from .controls import ControlLease
from .registry import BrowserRegistry
from ..config.live import (
    MAX_ACTION_BYTES,
    MAX_SEQUENCE_DIGITS,
    UPLOAD_TIMEOUT_SECONDS,
    CAMERA_UPLOAD_CHUNK_BYTES,
)
from ..media.output import owned_io
from ..routing.guard import local_route
from ..serialization import Json
from ..config.security import SETTINGS_PREFIX
from ..routing.request import read_document
from ..config.media.webcam import MAX_CAMERA_JPEG_BYTES
from ..config.messages.live import CAMERA_FRAME_WAIT, CAMERA_JPEG_REQUIRED, LIVE_SESSION_UNAVAILABLE


@dataclass(frozen=True, slots=True)
class LiveRoutes:
    """Authenticated local routes for preview frames, webcam input, and editing controls.

    Attributes:
        registry: Live sessions by lease identifier.
        is_multi_user: Whether the host serves several users, which turns the routes away.

    """

    registry: BrowserRegistry
    is_multi_user: bool = field(default=False, kw_only=True)

    async def exchange(self, request: web.Request) -> dict[str, Json]:
        """Read a size-limited request and exchange state with its owning session, which checks the capability.

        Args:
            request: The request that carries the exchange document.

        Returns:
            The status of the session.

        Raises:
            ConnectorError: When no session has the lease identifier.

        """
        document = await read_document(request)
        identifier = document.get('lease')
        with self.registry.lock:
            lease = self.registry.leases.get(identifier) if isinstance(identifier, str) else None
        if lease is None:
            raise ConnectorError(ErrorCode.UNAVAILABLE, LIVE_SESSION_UNAVAILABLE)
        return lease.exchange(document)

    def controls(self, identifier: str, capability: str) -> ControlLease:
        """Find a live editing session and verify its private capability.

        Args:
            identifier: The lease identifier of the session.
            capability: The capability value that the browser sent.

        Returns:
            The lease of the live editing session.

        Raises:
            ConnectorError: When no live editing session has the identifier.

        """
        with self.registry.lock:
            lease = self.registry.leases.get(identifier)
        if not isinstance(lease, ControlLease):
            raise ConnectorError(ErrorCode.UNAVAILABLE, LIVE_SESSION_UNAVAILABLE)
        lease.authorize(capability)
        return lease

    async def action(self, request: web.Request) -> dict[str, Json]:
        """Read and authorize a live editing action before queuing it.

        Args:
            request: The request that carries the action document.

        Returns:
            The reply that confirms the action.

        Raises:
            ConnectorError: When the lease identifier or the capability is not text.

        """
        document = await read_document(request, max_bytes=MAX_ACTION_BYTES)
        identifier, capability = document.get('lease'), document.get('capability')
        if not isinstance(identifier, str) or not isinstance(capability, str):
            raise ConnectorError(ErrorCode.UNAVAILABLE, LIVE_SESSION_UNAVAILABLE)
        return self.controls(identifier, capability).action(document)

    async def camera(self, request: web.Request) -> dict[str, Json]:
        """Authorize a single size-limited JPEG upload and decode it off the event loop.

        Args:
            request: The request that carries the JPEG frame and the lease headers.

        Returns:
            The reply that confirms the frame.

        Raises:
            ConnectorError: When the session has no webcam or the sequence header is not valid.
            web.HTTPRequestEntityTooLarge: When the upload passes the size limit.
            web.HTTPTooManyRequests: When another upload is still in progress.
            web.HTTPUnsupportedMediaType: When the content type is not JPEG.

        """
        lease = self.controls(
            request.headers.get('X-Reactor-Lease', ''),
            request.headers.get('X-Reactor-Capability', ''),
        )
        camera = lease.options.webcam
        sequence = request.headers.get('X-Reactor-Sequence', '')
        if camera is None or not sequence.isascii() or not sequence.isdecimal() or len(sequence) > MAX_SEQUENCE_DIGITS:
            raise ConnectorError(ErrorCode.UNAVAILABLE, LIVE_SESSION_UNAVAILABLE)
        if request.content_type != 'image/jpeg':
            raise web.HTTPUnsupportedMediaType(text=CAMERA_JPEG_REQUIRED)
        if not camera.upload_lock.acquire(blocking=False):
            raise web.HTTPTooManyRequests(text=CAMERA_FRAME_WAIT)
        try:
            payload = bytearray()
            async with asyncio.timeout(UPLOAD_TIMEOUT_SECONDS):
                async for chunk in request.content.iter_chunked(CAMERA_UPLOAD_CHUNK_BYTES):
                    payload.extend(chunk)
                    if len(payload) > MAX_CAMERA_JPEG_BYTES:
                        raise web.HTTPRequestEntityTooLarge(max_size=MAX_CAMERA_JPEG_BYTES, actual_size=len(payload))
            lease.authorize(request.headers.get('X-Reactor-Capability', ''))
            await owned_io(partial(camera.receive, bytes(payload), int(sequence)))
        finally:
            camera.upload_lock.release()
        return {'accepted': True}

    def register(self, routes: web.RouteTableDef) -> None:
        """Register live routes with the local mutation and host access guards.

        Args:
            routes: The route table that receives the live routes.

        """
        routes.post(SETTINGS_PREFIX + '/live/exchange')(
            local_route(self.exchange, is_mutation=True, is_multi_user=self.is_multi_user)
        )
        routes.post(SETTINGS_PREFIX + '/live/action')(
            local_route(self.action, is_mutation=True, is_multi_user=self.is_multi_user)
        )
        routes.post(SETTINGS_PREFIX + '/live/camera')(
            local_route(self.camera, is_mutation=True, is_multi_user=self.is_multi_user)
        )
