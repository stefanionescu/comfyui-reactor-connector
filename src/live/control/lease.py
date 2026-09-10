"""Accept a small set of live actions from the browser that owns a session."""

from typing import cast
from collections import deque
from ..state import LiveOptions
from ...language import translate
from ...serialization import Json
from ..lease import unavailable, BrowserLease
from ...errors import ErrorCode, ConnectorError
from ....config.generation.video import MAX_AUDIO_PROMPT_CHARACTERS
from ....config.live import MAX_SEQUENCE, MAX_PENDING_INPUTS, STALE_INPUT_SECONDS
from ....config.nodes import DEFAULT_POINTER_POSITION, MAX_POINTER_POSITION, MIN_POINTER_POSITION
from ....config.models.identities import (
    POINTER_MODELS,
    CONNECTION_TITLES,
    AUDIO_PROMPT_MODELS,
    EMPTY_PROMPT_MODELS,
)


class ControlLease(BrowserLease):
    """Authorize and order live editing actions from the client that owns the session."""

    def __init__(
        self,
        options: LiveOptions,
        *,
        choices: dict[str, tuple[str, ...]] | None = None,
        started: bool = False,
    ) -> None:
        """Create an owner-authorized live-action queue with model-specific options."""
        super().__init__(choices or {})
        self.options = options
        self.actions: deque[tuple[str, dict[str, Json], float]] = deque()
        self.action_sequence = -1
        self.started = started

    def invitation(self) -> dict[str, Json]:
        """Add supported live controls to the invitation sent to the owning client."""
        result = super().invitation()
        result.update(
            model_title=CONNECTION_TITLES[self.options.model],
            audio_prompt_limit=MAX_AUDIO_PROMPT_CHARACTERS,
            prompt=self.options.prompt,
            prompt_limit=self.options.prompt_limit,
            webcam=self.options.webcam is not None,
            pointer=self.options.model in POINTER_MODELS,
            audio_prompt=self.options.audio_prompt,
            sound=self.options.model in AUDIO_PROMPT_MODELS and self.options.audio_enabled,
        )
        return result

    def action(self, document: dict[str, Json]) -> dict[str, Json]:
        """Authorize, validate, and queue a strictly ordered live action."""
        self.authorize(document.get("capability"))
        if document.keys() != {"lease", "capability", "sequence", "action", "fields"}:
            raise unavailable()
        name, payload, sequence = document["action"], document["fields"], document["sequence"]
        if type(sequence) is not int or not 0 <= sequence <= MAX_SEQUENCE or not isinstance(payload, dict):
            raise unavailable()
        self._validate(name, payload)
        name = cast("str", name)
        with self.lock:
            if sequence <= self.action_sequence or self.closed or self.finishing or self.end:
                raise unavailable()
            if name != "start" and not self.controls_ready:
                raise unavailable()
            if name == "start":
                self.started = True
            else:
                # Keep release ordered after a press; replace only consecutive motion.
                if (
                    name == "pointer"
                    and self.actions
                    and self.actions[-1][0] == name
                    and payload.get("active") is True
                    and self.actions[-1][1].get("active") is True
                ):
                    self.actions.pop()
                if len(self.actions) >= MAX_PENDING_INPUTS:
                    raise ConnectorError(ErrorCode.UNAVAILABLE, translate("main", "errors.liveActionWait"))
                self.actions.append((name, payload, self.clock()))
            self.action_sequence = sequence
        return {"accepted": True}

    def _validate(self, name: Json, payload: dict[str, Json]) -> None:
        """Allow only supported action fields and values for this model."""
        valid = False
        if name == "start":
            valid = not payload
        elif name == "prompt":
            prompt = payload.get("prompt")
            valid = (
                payload.keys() == {"prompt"}
                and isinstance(prompt, str)
                and (bool(prompt.strip()) or self.options.model in EMPTY_PROMPT_MODELS)
                and len(prompt) <= self.options.prompt_limit
            )
        elif name == "audio_prompt":
            prompt = payload.get("prompt")
            valid = (
                self.options.model in AUDIO_PROMPT_MODELS
                and self.options.audio_enabled
                and payload.keys() == {"prompt"}
                and isinstance(prompt, str)
                and len(prompt) <= MAX_AUDIO_PROMPT_CHARACTERS
            )
        elif name == "pointer" and self.options.model in POINTER_MODELS:
            valid = (
                payload.keys() == {"x", "y", "active"}
                and type(payload.get("active")) is bool
                and all(
                    isinstance(value, (int, float))
                    and not isinstance(value, bool)
                    and MIN_POINTER_POSITION <= value <= MAX_POINTER_POSITION
                    for value in (payload.get("x"), payload.get("y"))
                )
            )
        if not valid:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.liveActionValues"))

    def is_ready(self) -> bool:
        """Require an active client, a start request, and any required webcam frames."""
        ready = super().is_ready()
        camera = self.options.webcam
        return ready and self.started and (camera is None or camera.is_ready())

    def take_action(self, name: str) -> dict[str, Json] | None:
        """Take the next action of one type, replacing a stale pointer press with a release."""
        with self.lock:
            for action in tuple(self.actions):
                kind, payload, received_at = action
                if kind == name:
                    self.actions.remove(action)
                    if kind == "pointer" and self.clock() - received_at > STALE_INPUT_SECONDS:
                        return {
                            "x": DEFAULT_POINTER_POSITION,
                            "y": DEFAULT_POINTER_POSITION,
                            "active": False,
                        }
                    return payload
            return None

    def finish(self) -> None:
        """Disable controls and discard actions while the recording finishes."""
        super().finish()
        with self.lock:
            self.actions.clear()

    def close(self, *, is_termination_confirmed: bool, failed: bool = False) -> None:
        """Record termination, discard actions, and clear retained webcam frames."""
        super().close(is_termination_confirmed=is_termination_confirmed, failed=failed)
        with self.lock:
            self.actions.clear()
        if self.options.webcam is not None:
            self.options.webcam.clear()
