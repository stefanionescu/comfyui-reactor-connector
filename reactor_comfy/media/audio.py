"""Load the WAV file created by the recording process as ComfyUI audio."""

import wave
from pathlib import Path
from typing import TypedDict

import numpy as np
from torch import Tensor, from_numpy

from ..errors import ConnectorError, ErrorCode


class NativeAudio(TypedDict):
    waveform: Tensor
    sample_rate: int


def load_audio(path: Path, maximum_bytes: int) -> NativeAudio:
    with wave.open(str(path), "rb") as reader:
        count, channels = reader.getnframes(), reader.getnchannels()
        if (
            channels not in (1, 2)
            or reader.getsampwidth() != 2
            or reader.getframerate() != 48_000
            or count < 1
            or count * channels * 4 > maximum_bytes // 2
        ):
            raise ConnectorError(
                ErrorCode.CAPTURE, "The recording audio exceeds its native limits."
            )
        data = reader.readframes(count)
        if len(data) != count * channels * 2:
            raise ConnectorError(ErrorCode.CAPTURE, "The recording audio is incomplete.")
    values = np.frombuffer(data, dtype="<i2").reshape(count, channels).T.astype(np.float32)
    values /= 32768
    return {"waveform": from_numpy(values).unsqueeze(0), "sample_rate": 48_000}
