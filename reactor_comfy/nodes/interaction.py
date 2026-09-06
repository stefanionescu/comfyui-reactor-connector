"""Invite only the browser that submitted the executing ComfyUI prompt."""

import asyncio
from typing import cast

from comfy.cli_args import args
from comfy_execution.utils import get_executing_context
from server import PromptServer

from ..errors import ConnectorError, ErrorCode
from ..live.control_interaction import ControlInteraction
from ..live.control_lease import ControlLease, LiveOptions
from ..live.interaction import CameraInteraction
from ..runtime import get_runtime


def _owner() -> tuple[str, str]:
    context = get_executing_context()
    if args.multi_user or context is None:
        raise ConnectorError(
            ErrorCode.UNAVAILABLE, "Live controls need a local, single-user ComfyUI browser."
        )
    running, _ = PromptServer.instance.prompt_queue.get_current_queue_volatile()
    for item in running:
        if len(item) >= 4 and item[1] == context.prompt_id and isinstance(item[3], dict):
            client = cast(dict[str, object], item[3]).get("client_id")
            if isinstance(client, str) and 1 <= len(client) <= 128:
                return client, context.node_id
    raise ConnectorError(ErrorCode.UNAVAILABLE, "The executing prompt has no browser owner.")


async def prepare_camera(model: str, prompt: str, duration_seconds: float) -> CameraInteraction:
    client, node = _owner()
    choices = {
        "movement": ("idle", "forward", "back", "strafe_left", "strafe_right"),
        "look_horizontal": ("idle", "left", "right"),
        "look_vertical": ("idle", "up", "down"),
    }
    if model == "reactor/lingbot-world-2":
        del choices["movement"]
        choices["move_longitudinal"] = ("idle", "forward", "back")
        choices["move_lateral"] = ("idle", "strafe_left", "strafe_right")
    elif model != "reactor/lingbot":
        raise ConnectorError(ErrorCode.UNAVAILABLE, "This model has no live camera adapter.")
    # Queuing a camera workflow starts it; the panel does not add another start step.
    lease = ControlLease(LiveOptions(model, prompt), choices=choices, started=True)
    get_runtime().browsers.add(lease)
    invitation = lease.invitation()
    invitation.update(model=model, node_id=node, duration_seconds=duration_seconds)
    PromptServer.instance.send_sync("reactor-inc.live", invitation, client)
    try:
        async with asyncio.timeout(5):
            while not lease.is_ready():
                if lease.read().end:
                    if lease.was_ended_by_user():
                        raise ConnectorError(ErrorCode.INTERRUPTED, "The live run was cancelled.")
                    raise ConnectorError(ErrorCode.UNAVAILABLE, "The live panel was closed.")
                await asyncio.sleep(0.05)
    except BaseException:
        lease.close(termination_confirmed=True, failed=True)
        raise
    return ControlInteraction(lease)


async def prepare_controls(options: LiveOptions, duration_seconds: float) -> ControlInteraction:
    client, node = _owner()
    lease = ControlLease(options)
    get_runtime().browsers.add(lease)
    invitation = lease.invitation()
    invitation.update(model=options.model, node_id=node, duration_seconds=duration_seconds)
    PromptServer.instance.send_sync("reactor-inc.controls", invitation, client)
    try:
        async with asyncio.timeout(60):
            while not lease.is_ready():
                if lease.read().end:
                    if lease.was_ended_by_user():
                        raise ConnectorError(ErrorCode.INTERRUPTED, "The live run was cancelled.")
                    raise ConnectorError(ErrorCode.UNAVAILABLE, "The live panel was closed.")
                await asyncio.sleep(0.05)
    except BaseException:
        lease.close(termination_confirmed=True, failed=True)
        raise
    return ControlInteraction(lease)
