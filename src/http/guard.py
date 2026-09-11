"""Apply the same local access and safe error rules to connector routes."""

from aiohttp import web
from ..serialization import Json
from ..errors import ConnectorError
from .security import require_local_request
from ...config.security import PRIVATE_HEADERS
from collections.abc import Callable, Awaitable
from ..language import translate, language_scope
from ..settings.conflict import SettingsConflictError


def local_route(
    callback: Callable[[web.Request], Awaitable[dict[str, Json]]],
    *,
    mutation: bool,
    multi_user: bool,
    response_key: str | None = None,
) -> Callable[[web.Request], Awaitable[web.Response]]:
    """Wrap a route with local-owner checks, safe errors, and private response headers."""

    async def respond(request: web.Request) -> web.Response:
        """Authorize the request and return only the route's public result or safe error."""
        with language_scope(request.headers.get("Accept-Language", "en")):
            try:
                require_local_request(request, mutation=mutation, multi_user=multi_user)
                result = await callback(request)
                return web.json_response(result[response_key] if response_key else result, headers=PRIVATE_HEADERS)
            except SettingsConflictError as error:
                message, status = str(error), 409
            except ConnectorError as error:
                message, status = str(error), 400
            except web.HTTPException as error:
                message, status = error.text, error.status
            except (OSError, UnicodeError):
                message, status = translate("main", "errors.stateUnreadable"), 500
            return web.json_response({"error": message}, status=status, headers=PRIVATE_HEADERS)

    return respond
