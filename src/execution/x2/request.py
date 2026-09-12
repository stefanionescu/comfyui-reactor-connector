"""Publish a local source to X2 after its editing controls are ready."""

from typing import ClassVar
from ...models import MODELS
from ...language import translate
from ..transport import Transport
from ..events import SessionEvents
from ...state.settings import Settings
from ..inputs import VideoInputOperation
from ..interaction import FramePublisher
from ...state.generation.x2 import X2Request
from ...state.session import RecordingWindow
from ...errors import ErrorCode, ConnectorError
from ...media.video.publish import VideoPublication
from ...serialization import mapping_value, validate_json
from ....config.generation.video import MAX_EDIT_PROMPT_CHARACTERS
from ....config.nodes import MAX_POINTER_POSITION, MIN_POINTER_POSITION


class X2Operation(VideoInputOperation[X2Request]):
    """Own source publication and pointer controls for one edit.

    Attributes:
        webcam: Optional browser camera that publishes source frames.
        publication: Owned source video publisher.

    """

    connection_name: ClassVar[str] = MODELS["x2"].connection_name

    def __init__(self, inputs: X2Request, *, webcam: FramePublisher | None = None) -> None:
        """Bind edit values, the optional webcam, and their source publication owner."""
        super().__init__(inputs)
        self.webcam = webcam
        self.publication = VideoPublication()

    def validate(self, settings: Settings) -> None:
        """Check the source, prompt, backlog option, and normalized pointer coordinates."""
        super().validate(settings)
        inputs = self.inputs
        if len(inputs.prompt) > MAX_EDIT_PROMPT_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.x2PromptLength"))
        if inputs.video is None and self.webcam is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.sourceVideoRequired"))
        if type(inputs.keep_backlog) is not bool or type(inputs.pointer_active) is not bool:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.pointerOptionType"))
        if any(
            type(value) not in (int, float) or not MIN_POINTER_POSITION <= value <= MAX_POINTER_POSITION
            for value in (inputs.pointer_x, inputs.pointer_y)
        ):
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.pointerCoordinates"))

    async def begin_generation(
        self, transport: Transport, events: SessionEvents, max_capture_seconds: float
    ) -> RecordingWindow:
        """Verify X2 commands, set the reference and pointer, and publish the source video."""
        del max_capture_seconds
        inputs = self.inputs
        if inputs.video is None and self.webcam is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, translate("main", "errors.sourceVideoRequired"))
        schema = await events.call("schema", transport.request_schema())
        _validate_contract(schema, transport)
        if inputs.image is not None:
            reference = await events.call(
                "upload", transport.upload_file(inputs.image, name="input.png", mime_type="image/png")
            )
            await events.command_reply("set_reference_image", {"reference_image": reference})
        await events.command_reply("set_keep_backlog", {"keep_backlog": inputs.keep_backlog})
        await events.command_reply(
            "set_pointer",
            {"x": inputs.pointer_x, "y": inputs.pointer_y, "active": inputs.pointer_active},
        )
        await events.command_reply("set_prompt", {"prompt": inputs.prompt})
        track = await events.call("publish_source", transport.publish_track("source"))
        if self.webcam is not None:
            await self.webcam.begin(track, events.on_error)
        elif inputs.video is not None:
            await self.publication.begin(inputs.video, track, events.on_error)
        self.publication.resume()
        return RecordingWindow(0, inputs.duration_seconds)

    async def release(self, transport: Transport) -> None:
        """Stop source publication and release the active pointer while connected."""
        await self.publication.close()
        if self.webcam is not None:
            await self.webcam.close()
        if self.inputs.pointer_active and transport.status == "ready":
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


__all__ = ["X2Operation"]
