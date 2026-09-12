"""Check shared video inputs and recording limits before starting a session."""

from typing import ClassVar
from ..language import translate
from .transport import Transport
from ...config.nodes import MAX_SEED
from ..state.settings import Settings
from ..state.session import ControlValues
from ..errors import ErrorCode, ConnectorError
from ..state.generation.inputs import VideoInputs
from ...config.media.video import DEFAULT_FRAME_RATE
from ..media.units import convert_mebibytes_to_bytes
from ...config.generation.session import MIN_CAPTURE_SECONDS, MAX_PROMPT_CHARACTERS


class VideoInputOperation[Request: VideoInputs]:
    """Validate shared request values and provide default session controls.

    Attributes:
        inputs: Immutable values supplied by the node.
        connection_name: Reviewed provider model connection.
        fallback_fps: Frame rate used when no timestamp is supplied.
        requires_audio: Whether the recording must contain audio.

    """

    connection_name: ClassVar[str]
    fallback_fps: ClassVar[int] = DEFAULT_FRAME_RATE
    requires_audio: ClassVar[bool] = False

    def __init__(self, inputs: Request) -> None:
        """Bind the immutable request to its execution owner."""
        self.inputs = inputs

    @property
    def prompt(self) -> str:
        """Expose the opening prompt to session control preparation."""
        return self.inputs.prompt

    @property
    def duration_seconds(self) -> float:
        """Expose the requested duration to the session owner."""
        return self.inputs.duration_seconds

    def build_control_values(self) -> ControlValues:
        """Return the standard browser-control values for this operation."""
        return ControlValues(
            self.inputs.prompt,
            is_passthrough_enabled=False,
            audio_prompt="",
            is_audio_enabled=False,
        )

    async def release(self, transport: Transport) -> None:
        """Models without held controls rely on the session owner's disconnect."""

    def validate(self, settings: Settings) -> None:
        """Check prompt, capture, and image limits before a connection."""
        inputs = self.inputs
        if type(inputs.prompt) is not str or not inputs.prompt.strip() or len(inputs.prompt) > MAX_PROMPT_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.promptLength"))
        validate_capture_inputs(inputs.duration_seconds, inputs.seed, settings)
        if inputs.image is not None and (
            type(inputs.image) is not bytes
            or not inputs.image
            or len(inputs.image) > convert_mebibytes_to_bytes(settings.max_upload_megabytes)
        ):
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.imageUploadLimit"))


def validate_capture_inputs(duration_seconds: float, seed: int, settings: Settings) -> None:
    """Validate capture length and seed without imposing a model's prompt policy."""
    if (
        type(duration_seconds) not in (int, float)
        or not MIN_CAPTURE_SECONDS <= duration_seconds <= settings.max_capture_seconds
    ):
        raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.captureLimit"))
    if type(seed) is not int or not 0 <= seed <= MAX_SEED:
        raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.seedRange"))


__all__ = ["VideoInputOperation", "validate_capture_inputs"]
