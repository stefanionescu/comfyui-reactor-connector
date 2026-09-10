"""Load the WAV file created by the recording process as ComfyUI audio."""

from __future__ import annotations

import wave
import torch
import numpy as np
from ..language import translate
from ..errors import ErrorCode, ConnectorError
from typing import cast, TypedDict, TYPE_CHECKING
from ...config.media.audio import SAMPLE_RATE, PCM_SAMPLE_BYTES

if TYPE_CHECKING:
    from pathlib import Path
    from torch import Tensor
    from numpy.typing import NDArray
    from collections.abc import Callable

    type AudioConversion = Callable[[NDArray[np.float32]], Tensor]


class NativeAudio(TypedDict):
    """ComfyUI audio samples with their sample rate."""

    waveform: Tensor
    sample_rate: int


def read_audio(path: Path, maximum_bytes: int) -> NativeAudio:
    """Load a size-limited PCM recording as normalized ComfyUI audio."""
    with wave.open(str(path), "rb") as reader:
        count, channels = reader.getnframes(), reader.getnchannels()
        if (
            channels not in (1, 2)
            or reader.getsampwidth() != PCM_SAMPLE_BYTES
            or reader.getframerate() != SAMPLE_RATE
            or count < 1
            or count * channels * 4 > maximum_bytes // 2
        ):
            raise ConnectorError(ErrorCode.CAPTURE, translate("main", "errors.audioLimit"))
        content = reader.readframes(count)
        if len(content) != count * channels * 2:
            raise ConnectorError(ErrorCode.CAPTURE, translate("main", "errors.audioIncomplete"))
    values = np.frombuffer(content, dtype="<i2").reshape(count, channels).T.astype(np.float32)
    values /= 32768
    from_numpy = cast("AudioConversion", torch.from_numpy)
    return {"waveform": from_numpy(values).unsqueeze(0), "sample_rate": SAMPLE_RATE}
