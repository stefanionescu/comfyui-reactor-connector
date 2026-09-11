"""Prepare the source video before asking SANA to edit it."""

import asyncio
from pathlib import Path
from ...models import MODELS
from ...language import translate
from ..transport import Transport
from .contract import source_mode
from typing import cast, ClassVar
from ..events import SessionEvents
from ...settings.schema import Settings
from ..operation import RecordingWindow
from ..interaction import FramePublisher
from dataclasses import field, dataclass
from ...errors import ErrorCode, ConnectorError
from ...media.video.publish import VideoPublication
from ..inputs import VideoInputs, validate_capture_inputs
from ....config.generation.session import MAX_PROMPT_CHARACTERS
from ....config.generation.video import MAX_ANCHOR_INTERVAL, MIN_ANCHOR_INTERVAL, DEFAULT_ANCHOR_INTERVAL


@dataclass(frozen=True, slots=True)
class SanaRequest(VideoInputs):
    """Edit an uploaded clip; source acceptance is separate from upload completion.

    Attributes:
        video: Optional prepared source video path.
        webcam: Optional live input frame publisher.
        anchor_interval: Number of chunks between anchors.
        publication: Owned source video publisher.

    """

    video: Path | None = None
    webcam: FramePublisher | None = None
    anchor_interval: int = DEFAULT_ANCHOR_INTERVAL
    connection_name: ClassVar[str] = MODELS["sana-streaming"].connection_name
    publication: VideoPublication = field(default_factory=VideoPublication, repr=False, compare=False)

    def validate(self, settings: Settings) -> None:
        """Check capture limits, source availability, prompt size, and anchor interval."""
        validate_capture_inputs(self.duration_seconds, self.seed, settings)
        if type(self.prompt) is not str or len(self.prompt) > MAX_PROMPT_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.sanaPromptLength"))
        if self.video is None and self.webcam is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.sourceVideoRequired"))
        if (
            type(self.anchor_interval) is not int
            or not MIN_ANCHOR_INTERVAL <= self.anchor_interval <= MAX_ANCHOR_INTERVAL
        ):
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.anchorInterval"))

    async def begin_generation(
        self, transport: Transport, events: SessionEvents, max_capture_seconds: float
    ) -> RecordingWindow:
        """Prepare the source using the declared model contract and start video editing."""
        del max_capture_seconds
        if self.video is None and self.webcam is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.sourceVideoRequired"))
        schema = await events.call("schema", transport.request_schema())
        mode = source_mode(schema, transport)
        if self.webcam is not None and mode != "camera":
            raise ConnectorError(ErrorCode.UNAVAILABLE, translate("main", "errors.sanaWebcamUnsupported"))
        if mode == "file":
            await self._accept_file(transport, events)
        await events.command_reply("set_seed", {"seed": self.seed})
        if self.prompt.strip():
            await events.command_reply("set_prompt", {"prompt": self.prompt})
        await events.command_reply("set_anchor_interval", {"chunks": self.anchor_interval})
        if mode == "file":
            await events.command_reply("set_mode", {"mode": "file"})
        else:
            track = await events.call("publish_camera", transport.publish_track("camera"))
            if self.webcam is not None:
                await self.webcam.begin(track, events.on_error)
            elif self.video is not None:
                await self.publication.begin(self.video, track, events.on_error)
        await events.command_reply("start", {})
        self.publication.resume()
        return RecordingWindow(0, self.duration_seconds)

    async def release(self, transport: Transport) -> None:
        """Stop source publication and close any webcam input."""
        del transport
        await self.publication.close()
        if self.webcam is not None:
            await self.webcam.close()

    async def _accept_file(self, transport: Transport, events: SessionEvents) -> None:
        """Upload the source and wait for model acceptance, then remove the temporary listener."""
        if self.video is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.sourceVideoRequired"))
        accepted = asyncio.Event()

        def observe(message: object) -> None:
            """Signal only a model state that confirms the uploaded video was accepted."""
            if not isinstance(message, dict):
                return
            document = cast("dict[str, object]", message)
            payload = document.get("data")
            if (
                document.get("type") == "state"
                and isinstance(payload, dict)
                and cast("dict[str, object]", payload).get("has_video") is True
            ):
                accepted.set()

        transport.on("message", observe)
        try:
            reference = await events.call(
                "upload", transport.upload_file(self.video, name="input.mp4", mime_type="video/mp4")
            )
            await events.command_reply("set_video", {"video": reference})
            await accepted.wait()
        finally:
            transport.off("message", observe)
