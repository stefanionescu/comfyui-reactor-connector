"""Serve one owner-checked exchange without exposing a general model-command proxy."""

import asyncio
from functools import partial

from aiohttp import web

from ..http_guard import local_route
from ..http_routes import PREFIX, read_document
from ..json_data import Json
from ..media.file_output import owned_io
from .control_lease import ControlLease
from .lease import BrowserRegistry, unavailable


class LiveRoutes:
    def __init__(self, registry: BrowserRegistry, *, multi_user: bool = False) -> None:
        self.registry = registry
        self.multi_user = multi_user

    async def exchange(self, request: web.Request) -> dict[str, Json]:
        return self.registry.exchange(await read_document(request))

    def controls(self, identifier: str, capability: str) -> ControlLease:
        with self.registry.lock:
            lease = self.registry.leases.get(identifier)
        if not isinstance(lease, ControlLease):
            raise unavailable()
        lease.authorize(capability)
        return lease

    async def action(self, request: web.Request) -> dict[str, Json]:
        document = await read_document(request, max_bytes=90_000)
        identifier, capability = document.get("lease"), document.get("capability")
        if not isinstance(identifier, str) or not isinstance(capability, str):
            raise unavailable()
        return self.controls(identifier, capability).action(document)

    async def camera(self, request: web.Request) -> dict[str, Json]:
        lease = self.controls(
            request.headers.get("X-Reactor-Lease", ""),
            request.headers.get("X-Reactor-Capability", ""),
        )
        camera = lease.options.webcam
        sequence = request.headers.get("X-Reactor-Sequence", "")
        if (
            camera is None
            or not sequence.isascii()
            or not sequence.isdecimal()
            or len(sequence) > 15
        ):
            raise unavailable()
        if request.content_type != "image/jpeg":
            raise web.HTTPUnsupportedMediaType(text="Send a camera JPEG.")
        if not camera.upload_lock.acquire(blocking=False):
            raise web.HTTPTooManyRequests(text="Wait for the previous camera frame.")
        try:
            data = bytearray()
            async with asyncio.timeout(2):
                async for chunk in request.content.iter_chunked(16_384):
                    data.extend(chunk)
                    if len(data) > 300_000:
                        raise web.HTTPRequestEntityTooLarge(max_size=300_000, actual_size=len(data))
            lease.authorize(request.headers.get("X-Reactor-Capability", ""))
            await owned_io(partial(camera.receive, bytes(data), int(sequence)))
        finally:
            camera.upload_lock.release()
        return {"accepted": True}

    def register(self, routes: web.RouteTableDef) -> None:
        routes.post(PREFIX + "/live/exchange")(
            local_route(self.exchange, mutation=True, multi_user=self.multi_user)
        )
        routes.post(PREFIX + "/live/action")(
            local_route(self.action, mutation=True, multi_user=self.multi_user)
        )
        routes.post(PREFIX + "/live/camera")(
            local_route(self.camera, mutation=True, multi_user=self.multi_user)
        )
