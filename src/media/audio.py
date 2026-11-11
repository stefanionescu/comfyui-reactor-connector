"""Load the WAV file created by the recording process as ComfyUI audio."""

from __future__ import annotations

import wave
from typing import TYPE_CHECKING, TypedDict, cast

import numpy as np
import torch

from ..errors import ErrorCode, ConnectorError
from ..config.media.audio import SAMPLE_RATE, MAX_CHANNELS, MIN_CHANNELS, PCM_SAMPLE_BYTES
from ..config.messages.media import AUDIO_LIMIT, AUDIO_INCOMPLETE

if TYPE_CHECKING:
    from pathlib import Path
    from collections.abc import Callable

    from torch import Tensor
    from numpy.typing import NDArray

    type AudioConversion = Callable[[NDArray[np.float32]], Tensor]


class NativeAudio(TypedDict):
    """ComfyUI audio samples with their sample rate.

    Attributes:
        waveform: The samples as a tensor with batch, channel, and sample axes.
        sample_rate: The number of samples per second.

    """

    waveform: Tensor
    sample_rate: int


def read_audio(path: Path, maximum_bytes: int) -> NativeAudio:
    """Load a size-limited pulse-code modulation (PCM) recording as normalized ComfyUI audio.

    Args:
        path: The WAV file to load.
        maximum_bytes: The memory budget for the decoded samples.

    Returns:
        The waveform and its sample rate.

    Raises:
        ConnectorError: When the file has an unsupported format, exceeds the budget, or is incomplete.

    """
    with wave.open(str(path), 'rb') as reader:
        count, channels = reader.getnframes(), reader.getnchannels()
        # Leave room for decoded samples and conversion buffers within the sample budget.
        if (
            not MIN_CHANNELS <= channels <= MAX_CHANNELS
            or reader.getsampwidth() != PCM_SAMPLE_BYTES
            or reader.getframerate() != SAMPLE_RATE
            or count < 1
            or count * channels * 4 > maximum_bytes // 2
        ):
            raise ConnectorError(ErrorCode.CAPTURE, AUDIO_LIMIT)
        content = reader.readframes(count)
        if len(content) != count * channels * PCM_SAMPLE_BYTES:
            raise ConnectorError(ErrorCode.CAPTURE, AUDIO_INCOMPLETE)
    values = np.frombuffer(content, dtype='<i2').reshape(count, channels).T.astype(np.float32)
    values /= 32768
    from_numpy = cast('AudioConversion', torch.from_numpy)
    return {'waveform': from_numpy(values).unsqueeze(0), 'sample_rate': SAMPLE_RATE}
