"""Serve one owner-checked exchange without exposing a general model-command proxy."""

import asyncio
from aiohttp import web
from functools import partial
from .lease import unavailable
from ..language import translate
from ..state.documents import Json
from ..media.output import owned_io
from ..http.guard import local_route
from .registry import BrowserRegistry
from .control.lease import ControlLease
from ..http.request import read_document
from ...config.routes import SETTINGS_PREFIX
from ...config.media.webcam import MAX_CAMERA_JPEG_BYTES
from ...config.live import (
    MAX_ACTION_BYTES,
    MAX_SEQUENCE_DIGITS,
    UPLOAD_TIMEOUT_SECONDS,
    CAMERA_UPLOAD_CHUNK_BYTES,
)


class LiveRoutes:
    """Authenticated local routes for preview frames, webcam input, and editing controls."""

    def __init__(self, registry: BrowserRegistry, *, is_multi_user: bool = False) -> None:
        """Bind the live-session registry and host access policy."""
        self.registry = registry
        self.is_multi_user = is_multi_user

    async def exchange(self, request: web.Request) -> dict[str, Json]:
        """Read a size-limited request and exchange state with its owning session."""
        return self.registry.exchange(await read_document(request))

    def controls(self, identifier: str, capability: str) -> ControlLease:
        """Find a live editing session and verify its private capability."""
        with self.registry.lock:
            lease = self.registry.leases.get(identifier)
        if not isinstance(lease, ControlLease):
            raise unavailable()
        lease.authorize(capability)
        return lease

    async def action(self, request: web.Request) -> dict[str, Json]:
        """Read and authorize a live editing action before queuing it."""
        document = await read_document(request, max_bytes=MAX_ACTION_BYTES)
        identifier, capability = document.get("lease"), document.get("capability")
        if not isinstance(identifier, str) or not isinstance(capability, str):
            raise unavailable()
        return self.controls(identifier, capability).action(document)

    async def camera(self, request: web.Request) -> dict[str, Json]:
        """Authorize a single size-limited JPEG upload and decode it off the event loop."""
        lease = self.controls(
            request.headers.get("X-Reactor-Lease", ""),
            request.headers.get("X-Reactor-Capability", ""),
        )
        camera = lease.options.webcam
        sequence = request.headers.get("X-Reactor-Sequence", "")
        if camera is None or not sequence.isascii() or not sequence.isdecimal() or len(sequence) > MAX_SEQUENCE_DIGITS:
            raise unavailable()
        if request.content_type != "image/jpeg":
            raise web.HTTPUnsupportedMediaType(text=translate("main", "errors.cameraJpegRequired"))
        if not camera.upload_lock.acquire(blocking=False):
            raise web.HTTPTooManyRequests(text=translate("main", "errors.cameraFrameWait"))
        try:
            payload = bytearray()
            async with asyncio.timeout(UPLOAD_TIMEOUT_SECONDS):
                async for chunk in request.content.iter_chunked(CAMERA_UPLOAD_CHUNK_BYTES):
                    payload.extend(chunk)
                    if len(payload) > MAX_CAMERA_JPEG_BYTES:
                        raise web.HTTPRequestEntityTooLarge(max_size=MAX_CAMERA_JPEG_BYTES, actual_size=len(payload))
            lease.authorize(request.headers.get("X-Reactor-Capability", ""))
            await owned_io(partial(camera.receive, bytes(payload), int(sequence)))
        finally:
            camera.upload_lock.release()
        return {"accepted": True}

    def register(self, routes: web.RouteTableDef) -> None:
        """Register live routes with the local mutation and host access guards."""
        routes.post(SETTINGS_PREFIX + "/live/exchange")(
            local_route(self.exchange, is_mutation=True, is_multi_user=self.is_multi_user)
        )
        routes.post(SETTINGS_PREFIX + "/live/action")(
            local_route(self.action, is_mutation=True, is_multi_user=self.is_multi_user)
        )
        routes.post(SETTINGS_PREFIX + "/live/camera")(
            local_route(self.camera, is_mutation=True, is_multi_user=self.is_multi_user)
        )
