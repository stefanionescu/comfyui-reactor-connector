from typing import ClassVar

from aiohttp import web

class PromptQueue:
    def get_current_queue_volatile(
        self,
    ) -> tuple[list[tuple[object, ...]], list[tuple[object, ...]]]: ...

class PromptServer:
    instance: ClassVar[PromptServer]
    routes: web.RouteTableDef
    app: web.Application
    prompt_queue: PromptQueue
    def send_sync(self, event: str, data: object, sid: str | None = None) -> None: ...
