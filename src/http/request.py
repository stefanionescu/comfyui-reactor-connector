"""Read JSON request bodies within local size and time limits."""

import asyncio
from aiohttp import web
from ..state.documents import Json
from ..serialization import parse_json, mapping_value
from ..config.settings import MAX_SETTINGS_BYTES, REQUEST_CHUNK_BYTES, SETTINGS_TIMEOUT_SECONDS
from ..config.messages.requests import REQUEST_TIMEOUT, REQUEST_ENCODING, REQUEST_TOO_LARGE, REQUEST_JSON_REQUIRED


async def read_document(request: web.Request, *, max_bytes: int = MAX_SETTINGS_BYTES) -> dict[str, Json]:
    """Read a size-limited JSON body, including without Content-Length."""
    if request.content_type != "application/json":
        raise web.HTTPUnsupportedMediaType(text=REQUEST_JSON_REQUIRED)
    if request.content_length is not None and request.content_length > max_bytes:
        raise web.HTTPRequestEntityTooLarge(
            max_size=max_bytes,
            actual_size=request.content_length,
            text=REQUEST_TOO_LARGE.format(max_bytes=max_bytes),
        )
    content = bytearray()
    try:
        async with asyncio.timeout(SETTINGS_TIMEOUT_SECONDS):
            async for chunk in request.content.iter_chunked(REQUEST_CHUNK_BYTES):
                content.extend(chunk)
                if len(content) > max_bytes:
                    raise web.HTTPRequestEntityTooLarge(
                        max_size=max_bytes,
                        actual_size=len(content),
                        text=REQUEST_TOO_LARGE.format(max_bytes=max_bytes),
                    )
    except TimeoutError:
        raise web.HTTPRequestTimeout(text=REQUEST_TIMEOUT) from None
    try:
        return mapping_value(parse_json(content.decode("utf-8"), max_bytes=max_bytes))
    except UnicodeError:
        raise web.HTTPBadRequest(text=REQUEST_ENCODING) from None
