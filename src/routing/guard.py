"""Apply the same local access and safe error rules to connector routes."""

from collections.abc import Callable, Awaitable

from aiohttp import web

from ..errors import ConnectorError
from .security import require_local_request
from ..serialization import Json
from ..config.security import PRIVATE_HEADERS
from ..settings.conflict import SettingsConflictError
from ..config.messages.settings import STATE_UNREADABLE


def local_route(
    callback: Callable[[web.Request], Awaitable[dict[str, Json]]],
    *,
    is_mutation: bool,
    is_multi_user: bool,
    response_key: str | None = None,
) -> Callable[[web.Request], Awaitable[web.Response]]:
    """Wrap a route with local-owner checks, safe errors, and private response headers.

    Args:
        callback: The route that builds the public result.
        is_mutation: Whether the route changes stored state.
        is_multi_user: Whether the host serves several users.
        response_key: The key of the result to send alone, or None to send the whole result.

    Returns:
        The guarded route handler.

    """

    async def respond(request: web.Request) -> web.Response:
        """Authorize the request and return only the route's public result or safe error.

        Args:
            request: The request to authorize and pass to the route.

        Returns:
            The JSON response with private headers.

        """
        try:
            require_local_request(request, is_mutation=is_mutation, is_multi_user=is_multi_user)
            result = await callback(request)
            return web.json_response(result[response_key] if response_key else result, headers=PRIVATE_HEADERS)
        except SettingsConflictError as error:
            message, status = str(error), 409
        except ConnectorError as error:
            message, status = str(error), 400
        except web.HTTPException as error:
            message, status = error.text, error.status
        except (OSError, UnicodeError):
            message, status = STATE_UNREADABLE, 500
        return web.json_response({'error': message}, status=status, headers=PRIVATE_HEADERS)

    return respond
