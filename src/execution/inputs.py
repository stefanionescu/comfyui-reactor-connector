"""Check shared video inputs and recording limits before starting a session."""

from typing import ClassVar
from ..language import translate
from .transport import Transport
from dataclasses import dataclass
from ...config.nodes import MAX_SEED
from .operation import ControlValues
from ..settings.settings import Settings
from ..errors import ErrorCode, ConnectorError
from ...config.media.video import DEFAULT_FRAME_RATE
from ..media.units import convert_mebibytes_to_bytes
from ...config.generation.session import MIN_CAPTURE_SECONDS, MAX_PROMPT_CHARACTERS


@dataclass(frozen=True, slots=True)
class VideoInputs:
    """Shared capture inputs; adapters add their own model restrictions.

    Attributes:
        prompt: Opening text sent to the model.
        duration_seconds: Requested recording length in seconds.
        seed: Random seed sent to the model.
        image: Optional encoded opening image.

    """

    prompt: str
    duration_seconds: float
    seed: int
    image: bytes | None = None
    model_name: ClassVar[str]
    fallback_fps: ClassVar[int] = DEFAULT_FRAME_RATE
    requires_audio: ClassVar[bool] = False

    def build_control_values(self) -> ControlValues:
        """Return the standard browser-control values for this operation."""
        return ControlValues(
            self.prompt,
            is_passthrough_enabled=False,
            audio_prompt="",
            is_audio_enabled=False,
        )

    async def release(self, transport: Transport) -> None:
        """Models without held controls rely on the session owner's disconnect."""

    def validate(self, settings: Settings) -> None:
        """Check prompt, capture, and image limits before a connection."""
        if type(self.prompt) is not str or not self.prompt.strip() or len(self.prompt) > MAX_PROMPT_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.promptLength"))
        validate_capture_inputs(self.duration_seconds, self.seed, settings)
        if self.image is not None and (
            type(self.image) is not bytes
            or not self.image
            or len(self.image) > convert_mebibytes_to_bytes(settings.max_upload_megabytes)
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
