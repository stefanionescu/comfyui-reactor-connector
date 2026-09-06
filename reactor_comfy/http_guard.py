"""Apply the same local access and safe error rules to connector routes."""

from collections.abc import Awaitable, Callable

from aiohttp import web

from .config_store import SettingsConflict
from .errors import ConnectorError
from .http_security import require_local_request
from .json_data import Json

PRIVATE_HEADERS = {"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"}


def local_route(
    handler: Callable[[web.Request], Awaitable[dict[str, Json]]],
    *,
    mutation: bool,
    multi_user: bool,
    response_key: str | None = None,
) -> Callable[[web.Request], Awaitable[web.Response]]:
    async def respond(request: web.Request) -> web.Response:
        try:
            require_local_request(request, mutation=mutation, multi_user=multi_user)
            result = await handler(request)
            result["mutation_allowed"] = not multi_user
            return web.json_response(
                result[response_key] if response_key else result, headers=PRIVATE_HEADERS
            )
        except SettingsConflict as error:
            return web.json_response({"error": str(error)}, status=409, headers=PRIVATE_HEADERS)
        except ConnectorError as error:
            return web.json_response({"error": str(error)}, status=400, headers=PRIVATE_HEADERS)
        except web.HTTPException as error:
            return web.json_response(
                {"error": error.text}, status=error.status, headers=PRIVATE_HEADERS
            )
        except (OSError, UnicodeError):
            return web.json_response(
                {"error": "Cannot read connector state. Check its location and permissions."},
                status=500,
                headers=PRIVATE_HEADERS,
            )

    return respond
