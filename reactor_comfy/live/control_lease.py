"""Accept a small set of live actions from the browser that owns a session."""

from collections import deque
from dataclasses import dataclass

from ..errors import ConnectorError, ErrorCode
from ..json_data import Json
from ..media.webcam import WebcamFrames
from .lease import BrowserLease, unavailable


@dataclass(frozen=True, slots=True)
class LiveOptions:
    model: str
    prompt: str
    webcam: WebcamFrames | None = None
    passthrough: bool = False
    audio_prompt: str = ""
    audio_enabled: bool = True

    @property
    def prompt_limit(self) -> int:
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
    def __init__(
        self,
        options: LiveOptions,
        *,
        choices: dict[str, tuple[str, ...]] | None = None,
        started: bool = False,
    ) -> None:
        super().__init__(choices or {})
        self.options = options
        self.actions: deque[tuple[str, dict[str, Json], float]] = deque()
        self.action_sequence = -1
        self.started = started

    def invitation(self) -> dict[str, Json]:
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
        self.authorize(document.get("capability"))
        if document.keys() != {"lease", "capability", "sequence", "action", "data"}:
            raise unavailable()
        name, data, sequence = document["action"], document["data"], document["sequence"]
        if type(sequence) is not int or not 0 <= sequence < 2**53 or not isinstance(data, dict):
            raise unavailable()
        self._validate(name, data)
        assert isinstance(name, str)
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
                    and data.get("active") is True
                    and self.actions[-1][1].get("active") is True
                ):
                    self.actions.pop()
                if len(self.actions) >= 8:
                    raise ConnectorError(
                        ErrorCode.UNAVAILABLE, "Wait for the previous live action."
                    )
                self.actions.append((name, data, self.clock()))
            self.action_sequence = sequence
        return {"accepted": True}

    def _validate(self, name: Json, data: dict[str, Json]) -> None:
        valid = False
        if name == "start":
            valid = not data
        elif name == "prompt":
            prompt = data.get("prompt")
            valid = (
                data.keys() == {"prompt"}
                and isinstance(prompt, str)
                and (bool(prompt.strip()) or self.options.model == "reactor/sana-streaming")
                and len(prompt) <= self.options.prompt_limit
            )
        elif name == "audio_prompt":
            prompt = data.get("prompt")
            valid = (
                self.options.model.startswith("reactor/visko-")
                and self.options.audio_enabled
                and data.keys() == {"prompt"}
                and isinstance(prompt, str)
                and len(prompt) <= 1000
            )
        elif name == "pointer" and self.options.model == "xmax/x2":
            valid = (
                data.keys() == {"x", "y", "active"}
                and type(data.get("active")) is bool
                and all(
                    isinstance(value, (int, float))
                    and not isinstance(value, bool)
                    and 0 <= value <= 1
                    for value in (data.get("x"), data.get("y"))
                )
            )
        if not valid:
            raise ConnectorError(
                ErrorCode.INVALID_INPUT, "Choose a supported live action and valid values."
            )

    def is_ready(self) -> bool:
        ready = super().is_ready()
        camera = self.options.webcam
        return ready and self.started and (camera is None or camera.is_ready())

    def take_action(self, name: str) -> dict[str, Json] | None:
        with self.lock:
            for action in tuple(self.actions):
                kind, data, received_at = action
                if kind == name:
                    self.actions.remove(action)
                    if kind == "pointer" and self.clock() - received_at > 0.75:
                        return {"x": 0.5, "y": 0.5, "active": False}
                    return data
            return None

    def finish(self) -> None:
        super().finish()
        with self.lock:
            self.actions.clear()

    def close(self, *, termination_confirmed: bool, failed: bool = False) -> None:
        super().close(termination_confirmed=termination_confirmed, failed=failed)
        with self.lock:
            self.actions.clear()
        if self.options.webcam is not None:
            self.options.webcam.clear()
