"""Check shared video inputs and recording limits before starting a session."""

from typing import Any, ClassVar
from dataclasses import dataclass
from collections.abc import Callable, Awaitable

from ..errors import ErrorCode, ConnectorError
from ..config.nodes import MAX_SEED, MAX_DURATION_SECONDS
from ..state.session import RecordingWindow
from ..state.settings import Settings
from ..config.settings import BYTES_PER_MEBIBYTE
from ..config.media.video import DEFAULT_FRAME_RATE
from ..config.messages.media import IMAGE_UPLOAD_LIMIT
from ..config.messages.inputs import SEED_RANGE, CAPTURE_LIMIT, PROMPT_LENGTH
from ..config.messages.session import SESSION_LIMIT_TOO_SHORT
from ..state.generation.inputs import VideoInputs
from ..config.generation.session import MIN_CAPTURE_SECONDS, MAX_PROMPT_CHARACTERS


@dataclass(eq=False, repr=False)
class VideoInputOperation[Request: VideoInputs]:
    """Validate shared request values for the session that runs the model.

    Attributes:
        inputs: Immutable values supplied by the node.
        connection_name: Reviewed provider model connection.
        begin_generation: Starts generation and returns the provider recording interval to save.
        default_fps: Frame rate the capture uses when the frames carry no timestamp.
        requires_audio: Whether the recording must contain audio.

    """

    inputs: Request
    connection_name: ClassVar[str]
    # Each model starts generation its own way, and returns the recording interval to save.
    begin_generation: ClassVar[Callable[..., Awaitable[RecordingWindow]]]
    default_fps: ClassVar[int] = DEFAULT_FRAME_RATE
    requires_audio: ClassVar[bool] = False

    def validate(self, settings: Settings) -> None:
        """Check prompt, capture, and image limits before a connection.

        Args:
            settings: The user settings that hold the session and upload limits.

        Raises:
            ConnectorError: When the prompt, the capture inputs, or the image breaks a limit.

        """
        inputs = self.inputs
        if not inputs.prompt.strip() or len(inputs.prompt) > MAX_PROMPT_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, PROMPT_LENGTH)
        validate_capture_inputs(inputs.duration_seconds, inputs.seed, settings)
        if inputs.image is not None and (
            not inputs.image or len(inputs.image) > settings.max_upload_megabytes * BYTES_PER_MEBIBYTE
        ):
            raise ConnectorError(ErrorCode.INVALID_INPUT, IMAGE_UPLOAD_LIMIT)


def validate_capture_inputs(duration_seconds: float, seed: int, settings: Settings) -> None:
    """Validate capture length and seed without imposing a model's prompt policy.

    Args:
        duration_seconds: The requested capture length, in seconds.
        seed: The requested random seed.
        settings: The user settings that hold the session time limit.

    Raises:
        ConnectorError: When the duration or the seed is out of range.

    """
    if not MIN_CAPTURE_SECONDS <= duration_seconds <= MAX_DURATION_SECONDS:
        raise ConnectorError(ErrorCode.INVALID_INPUT, CAPTURE_LIMIT)
    if duration_seconds >= settings.max_session_seconds:
        raise ConnectorError(ErrorCode.CONFIGURATION, SESSION_LIMIT_TOO_SHORT)
    if not 0 <= seed <= MAX_SEED:
        raise ConnectorError(ErrorCode.INVALID_INPUT, SEED_RANGE)


# The session owner runs any model operation, whatever its request type.
type VideoOperation = VideoInputOperation[Any]
