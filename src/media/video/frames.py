"""Decode prepared video frames while retaining one frame at a time."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import av

from ...errors import ErrorCode, ConnectorError
from ...config.media.video import MAX_FRAME_RATE, DEFAULT_FRAME_RATE
from ...config.messages.media import (
    SOURCE_FRAME_RATE,
    SOURCE_READER_CLOSED,
    SOURCE_FRAMES_MISSING,
    SOURCE_TIMESTAMP_MISSING,
)

if TYPE_CHECKING:
    from pathlib import Path
    from collections.abc import Iterator

    import numpy as np
    from numpy.typing import NDArray
    from av.container.input import InputContainer


class PreparedFrames:
    """Decode only connector-prepared media, keeping one decoded frame in memory."""

    def __init__(self, path: Path) -> None:
        """Prepare a reader for one connector-owned video file."""
        self.path = path
        self.container: InputContainer | None = None
        self.frames: Iterator[av.VideoFrame] | None = None
        self.step_seconds = 1 / DEFAULT_FRAME_RATE

    def open(self) -> tuple[NDArray[np.uint8], float]:
        """Open the prepared video and require a supported frame rate and a first timestamped frame."""
        self.container = av.open(str(self.path), mode='r')
        rate = self.container.streams.video[0].average_rate
        if rate is None or not 1 <= rate <= MAX_FRAME_RATE:
            raise ConnectorError(ErrorCode.INVALID_INPUT, SOURCE_FRAME_RATE)
        self.step_seconds = float(1 / rate)
        self.frames = iter(self.container.decode(video=0))
        first = self.next()
        if first is None:
            raise ConnectorError(ErrorCode.CAPTURE, SOURCE_FRAMES_MISSING)
        return first

    def next(self) -> tuple[NDArray[np.uint8], float] | None:
        """Decode the next red, green, and blue (RGB) frame and require its presentation timestamp."""
        if self.frames is None:
            raise ConnectorError(ErrorCode.CAPTURE, SOURCE_READER_CLOSED)
        frame = next(self.frames, None)
        if frame is None:
            return None
        if frame.pts is None or frame.time_base is None:
            raise ConnectorError(ErrorCode.CAPTURE, SOURCE_TIMESTAMP_MISSING)
        return cast('NDArray[np.uint8]', frame.to_ndarray(format='rgb24')), float(frame.pts * frame.time_base)

    def close(self) -> None:
        """Close the media container and release the frame iterator."""
        if self.container is not None:
            self.container.close()
        self.container = None
        self.frames = None
