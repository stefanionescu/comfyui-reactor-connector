"""Accept a small set of live actions from the browser that owns a session."""

from typing import cast
from collections import deque
from ...codes import ErrorCode
from ...serialization import Json
from dataclasses import dataclass
from ...errors import ConnectorError
from ...media.webcam import WebcamFrames
from ..lease import unavailable, BrowserLease
from ....config.generation.video import MAX_AUDIO_PROMPT_CHARACTERS
from ....config.live import MAX_PENDING_INPUTS, STALE_INPUT_SECONDS


@dataclass(frozen=True, slots=True)
class LiveOptions:
    """Model-specific prompts, sound options, and optional webcam input for a live session."""

    model: str
    prompt: str
    webcam: WebcamFrames | None = None
    passthrough: bool = False
    audio_prompt: str = ""
    audio_enabled: bool = True

    @property
    def prompt_limit(self) -> int:
        """Return the prompt character limit for the selected model."""
        if self.model == "reactor/fast-h3":
            return 800
        return (
            1000
            if self.model
            in (
                "xmax/x2",
                "reactor/lingbot",
                "reactor/lingbot-world-2",
                "reactor/visko-orbis-stable",
                "reactor/visko-orbis-dynamic",
            )
            else 20_000
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
            prompt=self.options.prompt,
            prompt_limit=self.options.prompt_limit,
            webcam=self.options.webcam is not None,
            pointer=self.options.model == "xmax/x2",
            audio_prompt=self.options.audio_prompt,
            sound=self.options.model.startswith("reactor/visko-") and self.options.audio_enabled,
        )
        return result

    def action(self, document: dict[str, Json]) -> dict[str, Json]:
        """Authorize, validate, and queue a strictly ordered live action."""
        self.authorize(document.get("capability"))
        if document.keys() != {"lease", "capability", "sequence", "action", "data"}:
            raise unavailable()
        name, payload, sequence = document["action"], document["data"], document["sequence"]
        if type(sequence) is not int or not 0 <= sequence < 2**53 or not isinstance(payload, dict):
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
                    raise ConnectorError(ErrorCode.UNAVAILABLE, "Wait for the previous live action.")
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
                and (bool(prompt.strip()) or self.options.model == "reactor/sana-streaming")
                and len(prompt) <= self.options.prompt_limit
            )
        elif name == "audio_prompt":
            prompt = payload.get("prompt")
            valid = (
                self.options.model.startswith("reactor/visko-")
                and self.options.audio_enabled
                and payload.keys() == {"prompt"}
                and isinstance(prompt, str)
                and len(prompt) <= MAX_AUDIO_PROMPT_CHARACTERS
            )
        elif name == "pointer" and self.options.model == "xmax/x2":
            valid = (
                payload.keys() == {"x", "y", "active"}
                and type(payload.get("active")) is bool
                and all(
                    isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= 1
                    for value in (payload.get("x"), payload.get("y"))
                )
            )
        if not valid:
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Choose a supported live action and valid values.")

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
                        return {"x": 0.5, "y": 0.5, "active": False}
                    return payload
            return None

    def finish(self) -> None:
        """Disable controls and discard actions while the recording finishes."""
        super().finish()
        with self.lock:
            self.actions.clear()

    def close(self, *, termination_confirmed: bool, failed: bool = False) -> None:
        """Record termination, discard actions, and clear retained webcam frames."""
        super().close(termination_confirmed=termination_confirmed, failed=failed)
        with self.lock:
            self.actions.clear()
        if self.options.webcam is not None:
            self.options.webcam.clear()
