"""Publish a local source to X2 after its editing controls are ready."""

from pathlib import Path
from typing import ClassVar
from ...models import MODELS
from ..inputs import VideoInputs
from ...language import translate
from ..transport import Transport
from ..events import SessionEvents
from ...settings.schema import Settings
from ..operation import RecordingWindow
from ..interaction import FramePublisher
from dataclasses import field, dataclass
from ...errors import ErrorCode, ConnectorError
from ...media.video.publish import VideoPublication
from ...serialization import mapping_value, validate_json
from ....config.generation.video import MAX_EDIT_PROMPT_CHARACTERS
from ....config.nodes import MAX_POINTER_POSITION, MIN_POINTER_POSITION, DEFAULT_POINTER_POSITION


@dataclass(frozen=True, slots=True)
class X2Request(VideoInputs):
    """Edit a clip using an optional reference image and a fixed pointer position.

    Attributes:
        video: Optional prepared source video path.
        webcam: Optional live input frame publisher.
        keep_backlog: Whether the provider retains queued source frames.
        pointer_active: Whether pointer control starts active.
        pointer_x: Normalized horizontal pointer position.
        pointer_y: Normalized vertical pointer position.
        publication: Owned source video publisher.

    """

    video: Path | None = None
    webcam: FramePublisher | None = None
    keep_backlog: bool = False
    pointer_active: bool = False
    pointer_x: float = DEFAULT_POINTER_POSITION
    pointer_y: float = DEFAULT_POINTER_POSITION
    connection_name: ClassVar[str] = MODELS["x2"].connection_name
    publication: VideoPublication = field(default_factory=VideoPublication, repr=False, compare=False)

    def validate(self, settings: Settings) -> None:
        """Check the source, prompt, backlog option, and normalized pointer coordinates."""
        super(X2Request, self).validate(settings)
        if len(self.prompt) > MAX_EDIT_PROMPT_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.x2PromptLength"))
        if self.video is None and self.webcam is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.sourceVideoRequired"))
        if type(self.keep_backlog) is not bool or type(self.pointer_active) is not bool:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.pointerOptionType"))
        if any(
            type(value) not in (int, float) or not MIN_POINTER_POSITION <= value <= MAX_POINTER_POSITION
            for value in (self.pointer_x, self.pointer_y)
        ):
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.pointerCoordinates"))

    async def begin_generation(
        self, transport: Transport, events: SessionEvents, max_capture_seconds: float
    ) -> RecordingWindow:
        """Verify X2 commands, set the reference and pointer, and publish the source video."""
        del max_capture_seconds
        if self.video is None and self.webcam is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.sourceVideoRequired"))
        schema = await events.call("schema", transport.request_schema())
        _validate_contract(schema, transport)
        if self.image is not None:
            reference = await events.call(
                "upload", transport.upload_file(self.image, name="input.png", mime_type="image/png")
            )
            await events.command_reply("set_reference_image", {"reference_image": reference})
        await events.command_reply("set_keep_backlog", {"keep_backlog": self.keep_backlog})
        await events.command_reply(
            "set_pointer",
            {"x": self.pointer_x, "y": self.pointer_y, "active": self.pointer_active},
        )
        await events.command_reply("set_prompt", {"prompt": self.prompt})
        track = await events.call("publish_source", transport.publish_track("source"))
        if self.webcam is not None:
            await self.webcam.begin(track, events.on_error)
        elif self.video is not None:
            await self.publication.begin(self.video, track, events.on_error)
        self.publication.resume()
        return RecordingWindow(0, self.duration_seconds)

    async def release(self, transport: Transport) -> None:
        """Stop source publication and release the active pointer while connected."""
        await self.publication.close()
        if self.webcam is not None:
            await self.webcam.close()
        if self.pointer_active and transport.status == "ready":
            await transport.send_command("set_pointer_active", {"pointer_active": False})


def _validate_contract(schema: object, transport: Transport) -> None:
    """Require the X2 edit commands and one send-only source video track."""
    document = mapping_value(validate_json(schema))
    paths = mapping_value(document.get("paths"))
    required = {
        "set_prompt",
        "set_reference_image",
        "set_keep_backlog",
        "set_pointer",
        "set_pointer_active",
    }
    commands = {
        name
        for name in required
        if mapping_value(mapping_value(paths.get(f"/events/{name}")).get("post")).get("operationId") == name
    }
    sources = [
        track
        for track in transport.tracks
        if track.name == "source" and track.kind == "video" and track.direction == "sendonly"
    ]
    if commands != required or len(sources) != 1:
        raise ConnectorError(ErrorCode.UNAVAILABLE, translate("main", "errors.x2Unsupported"))
