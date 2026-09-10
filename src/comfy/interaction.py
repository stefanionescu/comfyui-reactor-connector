"""Invite only the browser that submitted the executing ComfyUI prompt."""

import asyncio
from comfy.cli_args import args
from server import PromptServer
from ..language import translate
from ..serialization import Json
from ..runtime import get_runtime
from typing import cast, Protocol
from ..live.state import LiveOptions
from ..live.control.lease import ControlLease
from ..errors import ErrorCode, ConnectorError
from ..execution.operation import VideoOperation
from ..live.interaction import CameraInteraction
from ...config.generation.world import CAMERA_AXES
from comfy_execution.utils import get_executing_context
from ..execution.visko.request import ViskoStableRequest
from ...config.models.identities import MODEL_CAMERA_AXES
from ..live.control.interaction import ControlInteraction
from ...config.live import (
    INPUT_POLL_SECONDS,
    MIN_QUEUE_ITEM_FIELDS,
    MAX_CLIENT_ID_CHARACTERS,
    CAMERA_INVITATION_TIMEOUT_SECONDS,
    CONTROL_INVITATION_TIMEOUT_SECONDS,
)


class BrowserSender(Protocol):
    """Send a live-control invitation to its submitting browser."""

    def send_sync(self, event: str, payload: dict[str, Json], client: str) -> None:
        """Queue the event for one browser without blocking model execution."""
        raise NotImplementedError(event, payload, client)


def _owner() -> tuple[str, str]:
    """Find the executing prompt client and reject shared or unowned sessions."""
    context = get_executing_context()
    if args.multi_user or context is None:
        raise ConnectorError(ErrorCode.UNAVAILABLE, translate("main", "errors.liveHostRequirements"))
    running, _ = cast(
        "tuple[list[tuple[object, ...]], list[object]]",
        PromptServer.instance.prompt_queue.get_current_queue_volatile(),
    )
    for item in running:
        if len(item) >= MIN_QUEUE_ITEM_FIELDS and item[1] == context.prompt_id and isinstance(item[3], dict):
            client = cast("dict[str, object]", item[3]).get("client_id")
            if isinstance(client, str) and 1 <= len(client) <= MAX_CLIENT_ID_CHARACTERS:
                return client, context.node_id
    raise ConnectorError(ErrorCode.UNAVAILABLE, translate("main", "errors.browserOwnerMissing"))


async def wait_for_controls(lease: ControlLease, timeout_seconds: float) -> None:
    """Wait for the invited client within its setup deadline and report an explicit end request."""
    async with asyncio.timeout(timeout_seconds):
        while not lease.is_ready():
            if lease.read().end:
                if lease.was_ended_by_user():
                    raise ConnectorError(ErrorCode.INTERRUPTED, translate("main", "errors.liveCancelled"))
                raise ConnectorError(ErrorCode.UNAVAILABLE, translate("main", "errors.livePanelClosed"))
            await asyncio.sleep(INPUT_POLL_SECONDS)


async def prepare_camera(model: str, prompt: str, duration_seconds: float) -> CameraInteraction:
    """Invite the prompt owner to camera controls and await its connection."""
    client, node = _owner()
    axes = MODEL_CAMERA_AXES.get(model)
    if axes is None:
        raise ConnectorError(ErrorCode.UNAVAILABLE, translate("main", "errors.liveCameraUnsupported"))
    choices = {axis: tuple(CAMERA_AXES[axis]) for axis in axes}
    # Queuing a camera workflow starts it; the panel does not add another start step.
    lease = ControlLease(LiveOptions(model, prompt), choices=choices, started=True)
    get_runtime().browsers.add(lease)
    invitation = lease.invitation()
    invitation.update(model=model, node_id=node, duration_seconds=duration_seconds)
    cast("BrowserSender", PromptServer.instance).send_sync("reactor-inc.live", invitation, client)
    try:
        await wait_for_controls(lease, CAMERA_INVITATION_TIMEOUT_SECONDS)
    except BaseException:
        lease.close(is_termination_confirmed=True, failed=True)
        raise
    return ControlInteraction(lease)


async def prepare_controls(options: LiveOptions, duration_seconds: float) -> ControlInteraction:
    """Invite the prompt owner to editing controls and await its connection."""
    client, node = _owner()
    lease = ControlLease(options)
    get_runtime().browsers.add(lease)
    invitation = lease.invitation()
    invitation.update(model=options.model, node_id=node, duration_seconds=duration_seconds)
    cast("BrowserSender", PromptServer.instance).send_sync("reactor-inc.controls", invitation, client)
    try:
        await wait_for_controls(lease, CONTROL_INVITATION_TIMEOUT_SECONDS)
    except BaseException:
        lease.close(is_termination_confirmed=True, failed=True)
        raise
    return ControlInteraction(lease)


async def prepare_interaction(
    request: VideoOperation, *, interactive: bool, controls: LiveOptions | None
) -> CameraInteraction | ControlInteraction | None:
    """Open the camera or editing controls supported by this model request."""
    interaction = None
    if controls is not None:
        interaction = await prepare_controls(controls, request.duration_seconds)
    elif interactive:
        if request.model_name in MODEL_CAMERA_AXES:
            interaction = await prepare_camera(request.model_name, request.prompt, request.duration_seconds)
        else:
            options = LiveOptions(
                request.model_name,
                request.prompt,
                passthrough=request.prompt_passthrough if isinstance(request, ViskoStableRequest) else False,
                audio_prompt=request.audio_prompt if isinstance(request, ViskoStableRequest) else "",
                audio_enabled=request.audio_enabled if isinstance(request, ViskoStableRequest) else False,
            )
            interaction = await prepare_controls(options, request.duration_seconds)
    return interaction
