"""Publish a local source to X2 after its editing controls are ready."""

from pathlib import Path
from typing import ClassVar
from ..codes import ErrorCode
from .inputs import VideoInputs
from .transport import Transport
from .events import SessionEvents
from ..errors import ConnectorError
from ..media.webcam import WebcamFrames
from ..settings.settings import Settings
from dataclasses import field, dataclass
from ..media.video.publish import VideoPublication
from ..serialization import mapping_value, validate_json
from ...config.generation.video import MAX_EDIT_PROMPT_CHARACTERS


@dataclass(frozen=True, slots=True)
class X2Request(VideoInputs):
    """Edit a clip using an optional reference image and a fixed pointer position."""

    video: Path | None = None
    webcam: WebcamFrames | None = None
    keep_backlog: bool = False
    pointer_active: bool = False
    pointer_x: float = 0.5
    pointer_y: float = 0.5
    model_name: ClassVar[str] = "xmax/x2"
    publication: VideoPublication = field(default_factory=VideoPublication, repr=False, compare=False)

    def validate(self, settings: Settings) -> None:
        """Check the source, prompt, backlog option, and normalized pointer coordinates."""
        super(X2Request, self).validate(settings)
        if len(self.prompt) > MAX_EDIT_PROMPT_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Use at most 1,000 prompt characters.")
        if self.video is None and self.webcam is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Connect a prepared source video.")
        if type(self.keep_backlog) is not bool or type(self.pointer_active) is not bool:
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Use boolean backlog and pointer values.")
        if any(type(value) not in (int, float) or not 0 <= value <= 1 for value in (self.pointer_x, self.pointer_y)):
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Choose pointer coordinates from 0 to 1.")

    async def configure(self, transport: Transport, events: SessionEvents) -> None:
        """Verify X2 commands, set the reference and pointer, and publish the source video."""
        if self.video is None and self.webcam is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, "Connect a prepared source video.")
        schema = await events.call("schema", transport.request_schema())
        _validate_contract(schema, transport)
        if self.image is not None:
            reference = await events.call(
                "upload", transport.upload_file(self.image, name="input.png", mime_type="image/png")
            )
            await events.command("set_reference_image", {"reference_image": reference})
        await events.command("set_keep_backlog", {"keep_backlog": self.keep_backlog})
        await events.command(
            "set_pointer",
            {"x": self.pointer_x, "y": self.pointer_y, "active": self.pointer_active},
        )
        await events.command("set_prompt", {"prompt": self.prompt})
        track = await events.call("publish_source", transport.publish_track("source"))
        if self.webcam is not None:
            await self.webcam.begin(track, events.on_error)
        elif self.video is not None:
            await self.publication.begin(self.video, track, events.on_error)
        self.publication.resume()

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
        raise ConnectorError(ErrorCode.UNAVAILABLE, "This X2 input contract is unsupported. Check for an update.")
