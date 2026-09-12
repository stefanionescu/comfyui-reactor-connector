"""Invite only the browser that submitted the executing ComfyUI prompt."""

from __future__ import annotations

import asyncio
from comfy.cli_args import args
from server import PromptServer
from ..language import translate
from ..runtime import get_runtime
from ..live.options import LiveOptions
from ..models import MODELS_BY_CONNECTION
from ..live.control.lease import ControlLease
from ..errors import ErrorCode, ConnectorError
from typing import cast, Protocol, TYPE_CHECKING
from ...config.generation.world import CAMERA_AXES
from comfy_execution.utils import get_executing_context
from ..live.control.interaction import ControlInteraction
from ...config.live import (
    INPUT_POLL_SECONDS,
    MIN_QUEUE_ITEM_FIELDS,
    MAX_CLIENT_ID_CHARACTERS,
    CAMERA_INVITATION_TIMEOUT_SECONDS,
    CONTROL_INVITATION_TIMEOUT_SECONDS,
)


if TYPE_CHECKING:
    from ..state.documents import Json
    from ..media.webcam import WebcamFrames
    from ..execution.operation import VideoOperation
    from ..live.interaction import CameraInteraction


class _BrowserSender(Protocol):
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


async def _wait_for_controls(lease: ControlLease, timeout_seconds: float) -> None:
    """Wait for the invited client within its setup deadline and report an explicit end request."""
    async with asyncio.timeout(timeout_seconds):
        while not lease.is_ready():
            if lease.read().end:
                if lease.was_ended_by_user():
                    raise ConnectorError(ErrorCode.INTERRUPTED, translate("main", "errors.liveCancelled"))
                raise ConnectorError(ErrorCode.UNAVAILABLE, translate("main", "errors.livePanelClosed"))
            await asyncio.sleep(INPUT_POLL_SECONDS)


async def _prepare_camera(options: LiveOptions, duration_seconds: float) -> CameraInteraction:
    """Invite the prompt owner to camera controls and await its connection."""
    client, node = _owner()
    axes = MODELS_BY_CONNECTION[options.connection_name].camera_axes
    if not axes:
        raise ConnectorError(ErrorCode.UNAVAILABLE, translate("main", "errors.liveCameraUnsupported"))
    choices = {axis: tuple(CAMERA_AXES[axis]) for axis in axes}
    # Queuing a camera workflow starts it; the panel does not add another start step.
    lease = ControlLease(options, choices=choices, started=True)
    get_runtime().browsers.add(lease)
    invitation = lease.invitation()
    invitation.update(node_id=node, duration_seconds=duration_seconds)
    cast("_BrowserSender", PromptServer.instance).send_sync("reactor-inc.live", invitation, client)
    try:
        await _wait_for_controls(lease, CAMERA_INVITATION_TIMEOUT_SECONDS)
    except BaseException:
        lease.close(is_termination_confirmed=True, failed=True)
        raise
    return ControlInteraction(lease)


async def _prepare_controls(options: LiveOptions, duration_seconds: float) -> ControlInteraction:
    """Invite the prompt owner to editing controls and await its connection."""
    client, node = _owner()
    lease = ControlLease(options)
    get_runtime().browsers.add(lease)
    invitation = lease.invitation()
    invitation.update(node_id=node, duration_seconds=duration_seconds)
    cast("_BrowserSender", PromptServer.instance).send_sync("reactor-inc.controls", invitation, client)
    try:
        await _wait_for_controls(lease, CONTROL_INVITATION_TIMEOUT_SECONDS)
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
        interaction = await _prepare_controls(controls, request.duration_seconds)
    elif interactive:
        options = build_live_options(request)
        if MODELS_BY_CONNECTION[request.connection_name].camera_axes:
            interaction = await _prepare_camera(options, request.duration_seconds)
        else:
            interaction = await _prepare_controls(options, request.duration_seconds)
    return interaction


def build_live_options(request: VideoOperation, *, webcam: WebcamFrames | None = None) -> LiveOptions:
    """Translate execution-owned control values into live-session options."""
    values = request.build_control_values()
    return LiveOptions(
        request.connection_name,
        values.prompt,
        webcam,
        is_passthrough_enabled=values.is_passthrough_enabled,
        audio_prompt=values.audio_prompt,
        is_audio_enabled=values.is_audio_enabled,
    )


__all__ = ["build_live_options", "prepare_interaction"]
