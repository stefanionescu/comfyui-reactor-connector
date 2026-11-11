"""Serve private settings and credential changes through guarded local routes."""

import asyncio
from dataclasses import field, dataclass
from collections.abc import Callable, Awaitable

from aiohttp import web

from .store import ConfigurationStore
from ..routing.guard import local_route
from ..serialization import Json, mapping_value
from ..config.security import SETTINGS_PREFIX
from ..routing.request import read_document
from ..config.messages.requests import CLEAR_KEY_BODY, SINGLE_KEY_REQUIRED, SETTINGS_REVISION_REQUIRED

type Route = Callable[[web.Request], Awaitable[dict[str, Json]]]


@dataclass(frozen=True, slots=True)
class ConfigurationRoutes:
    """Register routes once during the host's extension load phase.

    Attributes:
        store: Private settings and credential store.
        is_multi_user: Whether the host serves several users, which makes the settings read-only.

    """

    store: ConfigurationStore
    is_multi_user: bool = field(default=False, kw_only=True)

    async def settings(self, request: web.Request) -> dict[str, Json]:
        """Validate a settings patch and save it against the caller's current revision.

        Args:
            request: The request whose body holds the revision and the changed settings.

        Returns:
            The status of the store after the change.

        Raises:
            web.HTTPBadRequest: When the body does not hold exactly a revision and settings.

        """
        document = await read_document(request)
        if document.keys() != {'revision', 'settings'} or not isinstance(document['revision'], str):
            raise web.HTTPBadRequest(text=SETTINGS_REVISION_REQUIRED)
        return await asyncio.to_thread(
            self.store.update_settings, mapping_value(document['settings']), document['revision']
        )

    async def credential(self, request: web.Request) -> dict[str, Json]:
        """Accept one API key and save it only through the private configuration store.

        Args:
            request: The request whose body holds the API key.

        Returns:
            The status of the store after the save.

        Raises:
            web.HTTPBadRequest: When the body does not hold exactly one API key.

        """
        document = await read_document(request)
        if document.keys() != {'api_key'} or not isinstance(document['api_key'], str):
            raise web.HTTPBadRequest(text=SINGLE_KEY_REQUIRED)
        return await asyncio.to_thread(self.store.save_credential, document['api_key'])

    async def clear_credential(self, request: web.Request) -> dict[str, Json]:
        """Remove the saved key after rejecting unexpected request content.

        Args:
            request: The request, which must have no body.

        Returns:
            The status of the store after the removal.

        Raises:
            web.HTTPBadRequest: When the request has a body.

        """
        if request.can_read_body:
            raise web.HTTPBadRequest(text=CLEAR_KEY_BODY)
        return await asyncio.to_thread(self.store.clear_credential)

    def _guard(self, route: Route, *, is_mutation: bool) -> Callable[[web.Request], Awaitable[web.Response]]:
        """Apply the host access policy to one route, and tell the editor whether the host permits changes.

        Args:
            route: The route to guard.
            is_mutation: Whether the route changes stored state.

        Returns:
            The guarded route handler.

        """

        async def respond(request: web.Request) -> dict[str, Json]:
            """Run the route and add the settings editor permission to its result.

            Args:
                request: The request to pass to the route.

            Returns:
                The result of the route, with the permission added.

            """
            result = await route(request)
            result['mutation_allowed'] = not self.is_multi_user
            return result

        return local_route(respond, is_mutation=is_mutation, is_multi_user=self.is_multi_user)

    def register(self, routes: web.RouteTableDef) -> None:
        """Register guarded status, settings, key-save, and key-removal endpoints.

        Args:
            routes: The route table of the host.

        """
        routes.get(SETTINGS_PREFIX + '/status')(
            self._guard(lambda _request: asyncio.to_thread(self.store.status), is_mutation=False)
        )
        routes.patch(SETTINGS_PREFIX + '/settings')(self._guard(self.settings, is_mutation=True))
        routes.put(SETTINGS_PREFIX + '/credential')(self._guard(self.credential, is_mutation=True))
        routes.delete(SETTINGS_PREFIX + '/credential')(self._guard(self.clear_credential, is_mutation=True))
