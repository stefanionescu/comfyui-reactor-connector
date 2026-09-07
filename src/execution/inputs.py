"""Check shared video inputs and recording limits before starting a session."""

from typing import ClassVar
from ..codes import ErrorCode
from .transport import Transport
from dataclasses import dataclass
from ..errors import ConnectorError
from ..settings.settings import Settings
from ...config.generation.session import MIN_CAPTURE_SECONDS, MAX_PROMPT_CHARACTERS


def validate_capture_inputs(duration_seconds: float, seed: int, settings: Settings) -> None:
    """Validate capture length and seed without imposing a model's prompt policy."""
    if (
        type(duration_seconds) not in (int, float)
        or not MIN_CAPTURE_SECONDS <= duration_seconds <= settings.max_capture_seconds
    ):
        raise ConnectorError(ErrorCode.INVALID_INPUT, "Choose a capture within the host limit.")
    if type(seed) is not int or not 0 <= seed <= 2**32 - 1:
        raise ConnectorError(ErrorCode.INVALID_INPUT, "Choose a seed from 0 to 4,294,967,295.")


@dataclass(frozen=True, slots=True)
class VideoInputs:
    """Shared capture inputs; adapters add their own model restrictions."""

    prompt: str
    duration_seconds: float
    seed: int
    image: bytes | None = None
    fallback_fps: ClassVar[int] = 24
    requires_audio: ClassVar[bool] = False

    @property
    def recording_start_seconds(self) -> float:
        """Start the saved interval at the beginning of the recording."""
        return 0

    @property
    def recording_duration_seconds(self) -> float:
        """Return the requested recording duration."""
        return self.duration_seconds

    async def release(self, transport: Transport) -> None:
        """Models without held controls rely on the session owner's disconnect."""

    def validate(self, settings: Settings) -> None:
        """Check prompt, capture, and image limits before a paid connection."""
        if type(self.prompt) is not str or not self.prompt.strip() or len(self.prompt) > MAX_PROMPT_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Enter a prompt of 1 to 20,000 characters.")
        validate_capture_inputs(self.duration_seconds, self.seed, settings)
        if self.image is not None and (
            type(self.image) is not bytes
            or not self.image
            or len(self.image) > settings.max_upload_megabytes * 1_048_576
        ):
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Provide image bytes within the upload limit.")
