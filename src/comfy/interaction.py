"""Invite only the browser that submitted the executing ComfyUI prompt."""

from __future__ import annotations

import asyncio
from comfy.cli_args import args
from server import PromptServer
from ..runtime import get_runtime
from ..live.options import LiveOptions
from ..live.controls import ControlLease
from ..models import MODELS_BY_CONNECTION
from ..errors import ErrorCode, ConnectorError
from ..live.interaction import LiveInteraction
from typing import cast, Protocol, TYPE_CHECKING
from ..config.generation.world import CAMERA_AXES
from comfy_execution.utils import get_executing_context
from ..config.live import (
    INPUT_POLL_SECONDS,
    MIN_QUEUE_ITEM_FIELDS,
    MAX_CLIENT_ID_CHARACTERS,
    CAMERA_INVITATION_TIMEOUT_SECONDS,
    CONTROL_INVITATION_TIMEOUT_SECONDS,
)
from ..config.messages.live import (
    LIVE_CANCELLED,
    LIVE_PANEL_CLOSED,
    BROWSER_OWNER_MISSING,
    LIVE_HOST_REQUIREMENTS,
)


if TYPE_CHECKING:
    from ..state.documents import Json
    from ..media.webcam import WebcamFrames
    from ..execution.operation import VideoOperation


class _BrowserSender(Protocol):
    """Send a live-control invitation to its submitting browser."""

    def send_sync(self, event: str, payload: dict[str, Json], client: str) -> None:
        """Queue the event for one browser without blocking model execution."""
        raise NotImplementedError(event, payload, client)


def _owner() -> tuple[str, str]:
    """Find the executing prompt client and reject shared or unowned sessions."""
    context = get_executing_context()
    if args.multi_user or context is None:
        raise ConnectorError(ErrorCode.UNAVAILABLE, LIVE_HOST_REQUIREMENTS)
    running, _ = cast(
        "tuple[list[tuple[object, ...]], list[object]]",
        PromptServer.instance.prompt_queue.get_current_queue_volatile(),
    )
    for item in running:
        if len(item) >= MIN_QUEUE_ITEM_FIELDS and item[1] == context.prompt_id and isinstance(item[3], dict):
            client = cast("dict[str, object]", item[3]).get("client_id")
            if isinstance(client, str) and 1 <= len(client) <= MAX_CLIENT_ID_CHARACTERS:
                return client, context.node_id
    raise ConnectorError(ErrorCode.UNAVAILABLE, BROWSER_OWNER_MISSING)


async def _wait_for_controls(lease: ControlLease, timeout_seconds: float) -> None:
    """Wait for the invited client within its setup deadline and report an explicit end operation."""
    async with asyncio.timeout(timeout_seconds):
        while not lease.is_ready():
            if lease.read().end:
                if lease.was_ended_by_user():
                    raise ConnectorError(ErrorCode.INTERRUPTED, LIVE_CANCELLED)
                raise ConnectorError(ErrorCode.UNAVAILABLE, LIVE_PANEL_CLOSED)
            await asyncio.sleep(INPUT_POLL_SECONDS)


async def _invite(
    options: LiveOptions,
    duration_seconds: float,
    *,
    event: str,
    timeout_seconds: float,
    choices: dict[str, tuple[str, ...]] | None = None,
) -> LiveInteraction:
    """Invite the prompt owner to the live panel and await its connection."""
    client, node = _owner()
    # Queuing a camera workflow starts it; the panel does not add another start step.
    lease = ControlLease(options, choices=choices, started=choices is not None)
    get_runtime().browsers.add(lease)
    try:
        invitation = lease.invitation()
        invitation.update(node_id=node, duration_seconds=duration_seconds)
        cast("_BrowserSender", PromptServer.instance).send_sync(event, invitation, client)
        await _wait_for_controls(lease, timeout_seconds)
    except BaseException:
        lease.close(is_termination_confirmed=True, failed=True)
        raise
    return LiveInteraction(lease)


async def prepare_interaction(
    operation: VideoOperation, *, interactive: bool, controls: LiveOptions | None
) -> LiveInteraction | None:
    """Open the camera or editing controls supported by this model operation."""
    if controls is not None:
        options = controls
    elif interactive:
        options = build_live_options(operation)
    else:
        return None
    axes = MODELS_BY_CONNECTION[options.connection_name].camera_axes
    if controls is None and axes:
        choices = {axis: tuple(CAMERA_AXES[axis]) for axis in axes}
        return await _invite(
            options,
            operation.duration_seconds,
            event="reactor-inc.live",
            timeout_seconds=CAMERA_INVITATION_TIMEOUT_SECONDS,
            choices=choices,
        )
    return await _invite(
        options,
        operation.duration_seconds,
        event="reactor-inc.controls",
        timeout_seconds=CONTROL_INVITATION_TIMEOUT_SECONDS,
    )


def build_live_options(operation: VideoOperation, *, webcam: WebcamFrames | None = None) -> LiveOptions:
    """Translate execution-owned control values into live-session options."""
    values = operation.build_control_values()
    return LiveOptions(
        operation.connection_name,
        values.prompt,
        webcam,
        is_passthrough_enabled=values.is_passthrough_enabled,
        audio_prompt=values.audio_prompt,
        is_audio_enabled=values.is_audio_enabled,
    )


__all__ = ["build_live_options", "prepare_interaction"]
