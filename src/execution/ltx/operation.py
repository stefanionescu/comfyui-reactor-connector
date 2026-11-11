"""Prepare a portrait and speech script for one LTX recording."""

from typing import ClassVar, override

from ..events import SessionEvents
from ..inputs import VideoInputOperation, validate_capture_inputs
from ...errors import ErrorCode, ConnectorError
from ...models import MODELS
from ..transport import SessionTransport
from ...state.session import RecordingWindow
from ...state.settings import Settings
from ...config.settings import BYTES_PER_MEBIBYTE
from ...state.generation.ltx import LtxSpeakRequest
from ...config.messages.media import PORTRAIT_REQUIRED, PORTRAIT_UPLOAD_LIMIT
from ...config.messages.inputs import (
    SPEECH_PACE,
    LTX_DURATION,
    SPEECH_LENGTH,
    LTX_SCENE_LENGTH,
    LTX_AUDIO_MISSING,
    SPEECH_PACE_RANGE,
    SPEECH_PACE_MISSING,
)
from ...config.generation.speech import (
    MIN_SPEECH_SECONDS,
    MAX_SCENE_CHARACTERS,
    MAX_WORDS_PER_MINUTE,
    MIN_WORDS_PER_MINUTE,
    MAX_SCRIPT_CHARACTERS,
    RECORDING_TAIL_SECONDS,
)


class LtxSpeakOperation(VideoInputOperation[LtxSpeakRequest]):
    """Prepare speech and a portrait before starting one take.

    Attributes:
        connection_name: The provider connection of the LTX model.
        requires_audio: Whether the saved take must contain audio.

    """

    connection_name: ClassVar[str] = MODELS['ltx2'].connection_name
    requires_audio: ClassVar[bool] = True

    @override
    def validate(self, settings: Settings) -> None:
        """Check the portrait, script, speech pace, and LTX recording limits.

        Args:
            settings: The user settings with the portrait upload limit.

        Raises:
            ConnectorError: When the duration, scene, script, pace, or portrait is invalid.

        """
        inputs = self.inputs
        validate_capture_inputs(inputs.duration_seconds, inputs.seed, settings)
        if inputs.duration_seconds < MIN_SPEECH_SECONDS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, LTX_DURATION)
        if len(inputs.prompt) > MAX_SCENE_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, LTX_SCENE_LENGTH)
        if not inputs.script.strip() or len(inputs.script) > MAX_SCRIPT_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, SPEECH_LENGTH)
        if not MIN_WORDS_PER_MINUTE <= inputs.words_per_minute <= MAX_WORDS_PER_MINUTE:
            raise ConnectorError(
                ErrorCode.INVALID_INPUT,
                SPEECH_PACE.format(minimum=MIN_WORDS_PER_MINUTE, maximum=MAX_WORDS_PER_MINUTE),
            )
        if not inputs.image or len(inputs.image) > settings.max_upload_megabytes * BYTES_PER_MEBIBYTE:
            raise ConnectorError(ErrorCode.INVALID_INPUT, PORTRAIT_UPLOAD_LIMIT)

    @override
    async def begin_generation(self, transport: SessionTransport, events: SessionEvents) -> RecordingWindow:
        """Upload the portrait and script, validate the offered speech pace, and start speech.

        Args:
            transport: The connected transport that lists tracks and uploads the portrait.
            events: The session events that send commands and hold the speech state.

        Returns:
            The recording interval for the requested duration.

        Raises:
            ConnectorError: When audio, the portrait, or a supported speech pace is missing.

        """
        inputs = self.inputs
        audio = [
            track
            for track in transport.get_client().tracks
            if track.name == 'main_audio' and track.kind == 'audio' and track.direction == 'recvonly'
        ]
        if len(audio) != 1:
            raise ConnectorError(ErrorCode.UNAVAILABLE, LTX_AUDIO_MISSING)
        if inputs.image is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, PORTRAIT_REQUIRED)
        reference = await events.call(
            'upload', transport.upload_file(inputs.image, name='input.png', mime_type='image/png')
        )
        await events.command_reply('set_avatar_image', {'avatar_image': reference})
        await events.command_reply('set_script', {'script': inputs.script})
        await events.call('speech_state', events.state_signals['state_update'].wait())
        state = events.latest_states['state_update']
        minimum, maximum = state.get('wpm_min'), state.get('wpm_max')
        if (
            not isinstance(minimum, (int, float))
            or isinstance(minimum, bool)
            or not isinstance(maximum, (int, float))
            or isinstance(maximum, bool)
            or not 0 < minimum <= maximum <= MAX_WORDS_PER_MINUTE
            or minimum != int(minimum)
            or maximum != int(maximum)
        ):
            raise ConnectorError(ErrorCode.UNAVAILABLE, SPEECH_PACE_MISSING)
        minimum, maximum = int(minimum), int(maximum)
        if not minimum <= inputs.words_per_minute <= maximum:
            raise ConnectorError(ErrorCode.INVALID_INPUT, SPEECH_PACE_RANGE.format(minimum=minimum, maximum=maximum))
        await events.command_reply('set_wpm', {'wpm': inputs.words_per_minute})
        # Recording fragments need later media to close after the requested capture ends.
        await events.command_reply(
            'set_duration_seconds',
            {'duration_seconds': inputs.duration_seconds + RECORDING_TAIL_SECONDS},
        )
        await events.command_reply('set_seed', {'seed': inputs.seed})
        if inputs.prompt.strip():
            await events.command_reply('set_prompt', {'prompt': inputs.prompt})
        await events.command_reply('start', {})
        return RecordingWindow(0, inputs.duration_seconds)
