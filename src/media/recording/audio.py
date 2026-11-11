"""Read, encode, and write the audio of a recording on its sample clock."""

from __future__ import annotations

import math
import wave
from typing import TYPE_CHECKING
from fractions import Fraction
from itertools import chain
from dataclasses import dataclass

import av
import numpy as np

from ...config.media.audio import (
    SAMPLE_RATE,
    MAX_CHANNELS,
    MIN_CHANNELS,
    PCM_SAMPLE_BYTES,
    AUDIO_WRITE_BLOCK_SAMPLES,
    AUDIO_ENCODE_BLOCK_SAMPLES,
)

if TYPE_CHECKING:
    from pathlib import Path

    from numpy.typing import NDArray
    from av.container.output import OutputContainer


@dataclass(frozen=True, slots=True)
class RecordingAudio:
    """Normalized audio samples and their channel layout.

    Attributes:
        samples: Planar float32 audio samples.
        layout: Mono or stereo channel layout.

    """

    samples: NDArray[np.float32]
    layout: str


class AudioEncoder:
    """Interleave timestamped audio while video advances, then finish its exact interval."""

    def __init__(self, writer: OutputContainer, audio: RecordingAudio) -> None:
        """Configure an Advanced Audio Coding (AAC) stream on the shared recording sample clock.

        Args:
            writer: The output file that receives the audio stream.
            audio: The samples to encode.

        """
        self.writer = writer
        self.audio = audio
        self.position = 0
        self.stream = writer.add_stream('aac', rate=SAMPLE_RATE)  # pyright: ignore[reportUnknownMemberType] # reason: PyAV's stubs leave Packet without its stream type.
        self.stream.layout = audio.layout
        self.stream.time_base = Fraction(1, SAMPLE_RATE)

    def encode_until(self, end_sample: int) -> None:
        """Encode audio up to the requested sample position in small consecutive blocks.

        Args:
            end_sample: The sample position at which to stop.

        """
        end = min(end_sample, self.audio.samples.shape[1])
        while self.position < end:
            stop = min(end, self.position + AUDIO_ENCODE_BLOCK_SAMPLES)
            values = np.ascontiguousarray(self.audio.samples[:, self.position : stop])
            frame = av.AudioFrame.from_ndarray(values, format='fltp', layout=self.audio.layout)
            frame.rate = SAMPLE_RATE
            frame.time_base = Fraction(1, SAMPLE_RATE)
            frame.pts = self.position
            self.writer.mux(self.stream.encode(frame))  # pyright: ignore[reportUnknownMemberType] # reason: PyAV's stubs leave Packet without its stream type.
            self.position = stop


def copy_audio_frame(
    frame: av.AudioFrame,
    samples: NDArray[np.float32],
    origin: Fraction,
    previous_end: int | None,
) -> tuple[int, int, bool]:
    """Copy nonoverlapping audio and return its end, copied sample count, and interval completion.

    Args:
        frame: The resampled audio frame.
        samples: The buffer that receives the samples.
        origin: The recording time of the first selected video frame.
        previous_end: The end position of the frame before, or None.

    Returns:
        The end position, the copied sample count, and whether the interval is complete.

    Raises:
        ValueError: When the frame has no timestamp, overlaps the frame before, or holds values that are not finite.

    """
    if frame.pts is None or frame.time_base is None:
        message = 'recording_audio'
        raise ValueError(message)
    start = round((frame.pts * frame.time_base - origin) * SAMPLE_RATE)
    end = start + frame.samples
    if previous_end is not None and start < previous_end:
        message = 'recording_audio'
        raise ValueError(message)
    count = samples.shape[1]
    left, right = max(0, start), min(count, end)
    copied = 0
    if left < right:
        values = frame.to_ndarray()
        if not np.isfinite(values).all():
            message = 'recording_audio'
            raise ValueError(message)
        samples[:, left:right] = values[:, left - start : right - start]
        copied = right - left
    return end, copied, start >= count


def read_audio(source: Path, origin: Fraction, duration_seconds: float, maximum_memory: int) -> RecordingAudio:
    """Use media timestamps, preserve gaps, and reject overlapping audio frames.

    Args:
        source: The recording file.
        origin: The recording time at which the interval starts.
        duration_seconds: The length of the interval.
        maximum_memory: The memory budget for the samples.

    Returns:
        The samples and their channel layout.

    Raises:
        ValueError: When the audio is missing, unsupported, or too large for the budget.

    """
    with (
        source.open('rb') as file,
        av.open(file, mode='r', format='mp4', options={'protocol_whitelist': 'pipe'}) as reader,
    ):
        if len(reader.streams.audio) != 1:
            message = 'recording_audio'
            raise ValueError(message)
        stream = reader.streams.audio[0]
        channels = len(stream.codec_context.layout.channels)
        if not MIN_CHANNELS <= channels <= MAX_CHANNELS:
            message = 'recording_audio'
            raise ValueError(message)
        layout = 'mono' if channels == 1 else 'stereo'
        count = math.ceil(duration_seconds * SAMPLE_RATE)
        # Reserve half the sample budget for conversion buffers; this is not a process memory cap.
        if count * channels * 4 > maximum_memory // 2:
            message = 'recording_memory'
            raise ValueError(message)
        samples = np.zeros((channels, count), dtype=np.float32)
        resampler = av.AudioResampler(format='fltp', layout=layout, rate=SAMPLE_RATE)
        previous_end: int | None = None
        copied = 0

        converted = chain.from_iterable(resampler.resample(frame) for frame in chain(reader.decode(stream), (None,)))
        for frame in converted:
            previous_end, accepted, finished = copy_audio_frame(frame, samples, origin, previous_end)
            copied += accepted
            if finished:
                break
        if copied == 0:
            message = 'recording_audio'
            raise ValueError(message)
        return RecordingAudio(samples, layout)


def write_wav(path: Path, audio: RecordingAudio, count: int, maximum_bytes: int) -> None:
    """Write the selected samples as size-limited signed 16-bit pulse-code modulation (PCM) audio.

    Args:
        path: The WAV file to write.
        audio: The samples to write.
        count: The number of samples to keep per channel.
        maximum_bytes: The largest file to write.

    Raises:
        ValueError: When the file exceeds its size limit.

    """
    if count * audio.samples.shape[0] * PCM_SAMPLE_BYTES + 44 > maximum_bytes:
        message = 'file_limit'
        raise ValueError(message)
    with wave.open(str(path), 'wb') as output:
        output.setnchannels(audio.samples.shape[0])
        output.setsampwidth(PCM_SAMPLE_BYTES)
        output.setframerate(SAMPLE_RATE)
        for start in range(0, count, AUDIO_WRITE_BLOCK_SAMPLES):
            chunk = audio.samples[:, start : min(count, start + AUDIO_WRITE_BLOCK_SAMPLES)]
            pcm = np.rint(np.clip(chunk, -1, 1) * 32767).astype('<i2')
            output.writeframes(pcm.T.tobytes())
