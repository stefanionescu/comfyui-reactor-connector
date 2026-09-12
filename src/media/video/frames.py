"""Decode prepared video frames while retaining one frame at a time."""

from __future__ import annotations

import av
from ...language import translate
from typing import cast, TYPE_CHECKING
from ...errors import ErrorCode, ConnectorError
from ....config.media.video import DEFAULT_FRAME_RATE, MAX_FRAME_RATE

if TYPE_CHECKING:
    import numpy as np
    from pathlib import Path
    from numpy.typing import NDArray
    from collections.abc import Iterator
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
        self.container = av.open(str(self.path), mode="r")
        rate = self.container.streams.video[0].average_rate
        if rate is None or not 1 <= rate <= MAX_FRAME_RATE:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.sourceFrameRate"))
        self.step_seconds = float(1 / rate)
        self.frames = iter(self.container.decode(video=0))
        first = self.next()
        if first is None:
            raise ConnectorError(ErrorCode.CAPTURE, translate("main", "errors.sourceFramesMissing"))
        return first

    def next(self) -> tuple[NDArray[np.uint8], float] | None:
        """Decode the next RGB frame and require its presentation timestamp."""
        if self.frames is None:
            raise ConnectorError(ErrorCode.CAPTURE, translate("main", "errors.sourceReaderClosed"))
        frame = next(self.frames, None)
        if frame is None:
            return None
        if frame.pts is None or frame.time_base is None:
            raise ConnectorError(ErrorCode.CAPTURE, translate("main", "errors.sourceTimestampMissing"))
        return cast("NDArray[np.uint8]", frame.to_ndarray(format="rgb24")), float(frame.pts * frame.time_base)

    def close(self) -> None:
        """Close the media container and release the frame iterator."""
        if self.container is not None:
            self.container.close()
        self.container = None
        self.frames = None
