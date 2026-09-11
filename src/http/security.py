"""Restrict private configuration routes to the local ComfyUI origin."""

import ipaddress
from aiohttp import web
from typing import cast
from ..language import translate
from urllib.parse import SplitResult, urlsplit


def _has_forwarding_headers(request: web.Request) -> bool:
    """Reject proxy metadata because private routes require a direct local connection."""
    return any(
        name.lower() in {"forwarded", "x-real-ip"} or name.lower().startswith("x-forwarded-")
        for name in request.headers
    )


def _is_local_url(target: SplitResult) -> bool:
    """Require a bare loopback host without user information or URL suffixes."""
    return all(
        (
            target.hostname in {"localhost", "127.0.0.1", "::1"},
            target.username is None,
            target.password is None,
            not target.path,
            not target.query,
            not target.fragment,
        )
    )


def _is_local_target(request: web.Request, target: SplitResult, port: int) -> bool:
    """Match a loopback peer and URL to the server socket receiving the request."""
    peer = ipaddress.ip_address(request.remote or "")
    socket = request.transport.get_extra_info("sockname") if request.transport else None
    address = cast("tuple[object, ...]", socket) if isinstance(socket, tuple) else ()
    socket_port = address[1] if len(address) > 1 else None
    return peer.is_loopback and _is_local_url(target) and port == socket_port


def _is_same_origin(origin: str, target: SplitResult, port: int) -> bool:
    """Accept only an origin with the request's exact scheme, host, and effective port."""
    source = urlsplit(origin)
    source_port = source.port or (443 if source.scheme == "https" else 80)
    return all(
        (
            source.scheme == target.scheme,
            source.hostname == target.hostname,
            source_port == port,
            source.path in ("", "/"),
            source.username is None,
            source.password is None,
            not source.query,
            not source.fragment,
        )
    )


def require_local_request(request: web.Request, *, is_mutation: bool, is_multi_user: bool) -> None:
    """Reject remote peers, rebinding hosts, cross-origin requests, and unsafe writes."""
    forbidden = web.HTTPForbidden(text=translate("main", "errors.localConnectionRequired"))
    try:
        if _has_forwarding_headers(request):
            raise forbidden
        target = urlsplit(f"{request.scheme}://{request.host}")
        port = target.port or (443 if request.secure else 80)
        if not _is_local_target(request, target, port):
            raise forbidden
        origin = request.headers.get("Origin")
        if origin is not None and not _is_same_origin(origin, target, port):
            raise forbidden
        if request.headers.get("Sec-Fetch-Site") in {"cross-site", "same-site"}:
            raise forbidden
        if is_mutation and (is_multi_user or request.headers.get("X-Reactor-Comfy") != "1"):
            raise forbidden
    except ValueError:
        raise forbidden from None
