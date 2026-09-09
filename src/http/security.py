"""Restrict private configuration routes to the local ComfyUI origin."""

import ipaddress
from aiohttp import web
from typing import cast
from ..language import translate
from urllib.parse import urlsplit


def require_local_request(request: web.Request, *, mutation: bool, multi_user: bool) -> None:
    """Reject remote peers, rebinding hosts, cross-origin requests, and unsafe writes."""
    forbidden = web.HTTPForbidden(text=translate("main", "errors.localConnectionRequired"))
    try:
        if any(
            name.lower() in {"forwarded", "x-real-ip"} or name.lower().startswith("x-forwarded-")
            for name in request.headers
        ):
            raise forbidden
        peer = ipaddress.ip_address(request.remote or "")
        target = urlsplit(f"{request.scheme}://{request.host}")
        is_host_valid = (
            target.hostname in {"localhost", "127.0.0.1", "::1"}
            and target.username is None
            and target.password is None
            and not target.path
            and not target.query
            and not target.fragment
        )
        port = target.port or (443 if request.secure else 80)
        socket = request.transport.get_extra_info("sockname") if request.transport else None
        address = cast("tuple[object, ...]", socket) if isinstance(socket, tuple) else ()
        socket_port = address[1] if len(address) > 1 else None
        if not peer.is_loopback or not is_host_valid or port != socket_port:
            raise forbidden
        origin = request.headers.get("Origin")
        if origin is not None:
            source = urlsplit(origin)
            if (
                source.scheme != target.scheme
                or source.hostname != target.hostname
                or (source.port or (443 if source.scheme == "https" else 80)) != port
                or source.path not in ("", "/")
                or source.username is not None
                or source.password is not None
                or source.query
                or source.fragment
            ):
                raise forbidden
        if request.headers.get("Sec-Fetch-Site") in {"cross-site", "same-site"}:
            raise forbidden
        if mutation and (multi_user or request.headers.get("X-Reactor-Comfy") != "1"):
            raise forbidden
    except ValueError:
        raise forbidden from None
