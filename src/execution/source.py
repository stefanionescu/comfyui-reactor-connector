"""Hold the webcam and the source publication that an editing session reads."""

from .inputs import VideoInputOperation
from ..media.webcam import WebcamFrames
from ..media.video.publish import VideoPublication
from ..state.generation.inputs import VideoInputs


class SourceVideoOperation[Request: VideoInputs](VideoInputOperation[Request]):
    """Keep the source of an edit: a browser camera, or a file that the operation publishes."""

    def __init__(self, inputs: Request, *, webcam: WebcamFrames | None = None) -> None:
        """Bind the request values, the optional webcam, and the owner of the source publication.

        Args:
            inputs: The request values from the node.
            webcam: The browser camera that supplies source frames, or None for a file.

        """
        super().__init__(inputs)
        self.webcam = webcam
        self.publication = VideoPublication()
