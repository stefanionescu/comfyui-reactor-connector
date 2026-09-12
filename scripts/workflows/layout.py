"""Place each example's instructions, controls, and previews in reading order."""

import re
import math
import textwrap
from ...src.state.documents import Json
from .example import (
    Example,
    FIRST_STEP_ID,
    GENERATION_ID,
    SAVE_AUDIO_ID,
    SAVE_VIDEO_ID,
    SETUP_NOTE_ID,
    USAGE_NOTE_ID,
    EXTRA_INPUT_ID,
    SECOND_STEP_ID,
    SOURCE_INPUT_ID,
)

GAP = 60
INPUT_WIDTH = 400
MODEL_WIDTH = 440
OUTPUT_WIDTH = 360


def note_height(text: str, width: int) -> int:
    """Allow for the native note's font, wrapped lines, and paragraph margins."""
    height = 20
    for paragraph in text.split("\n\n"):
        plain = re.sub(r"[*`#]", "", paragraph)
        lines = sum(max(1, len(textwrap.wrap(line, int((width - 32) / 5.5)))) for line in plain.splitlines())
        height += lines * 14 + 10
    return math.ceil(height / 20) * 20


def model_height(example: Example, model: str) -> int:
    """Reserve prompt space and the controls used by this model."""
    choices = (
        (example.clip_count > 1, 460),
        (model.startswith("visko"), 470),
        (model == "ltx2", 410),
        (model.startswith("lingbot"), 420),
        (model == "x2" and example.mode != "webcam", 360),
    )
    return next((height for applies, height in choices if applies), 330)


def arrange(nodes: list[Json], example: Example, model: str) -> dict[str, Json]:
    """Align columns while keeping each note and node sized for its content."""
    records = [item for item in nodes if isinstance(item, dict)]
    by_id = {item["id"]: item for item in records if isinstance(item["id"], int)}
    has_inputs = any(number in by_id for number in (SOURCE_INPUT_ID, EXTRA_INPUT_ID, SECOND_STEP_ID))
    model_x = 40 + INPUT_WIDTH + GAP if has_inputs else 40
    output_x = model_x + MODEL_WIDTH + GAP
    first_width = INPUT_WIDTH if has_inputs else MODEL_WIDTH
    top = 60
    note_columns = (
        (SETUP_NOTE_ID, 40, first_width),
        (USAGE_NOTE_ID, model_x if has_inputs else output_x, MODEL_WIDTH if has_inputs else OUTPUT_WIDTH),
    )
    for number, x, width in (column for column in note_columns if column[0] in by_id):
        note = by_id[number]
        widgets = note["widgets_values"]
        if isinstance(widgets, list) and isinstance(widgets[0], str):
            height = note_height(widgets[0], width)
            note["pos"], note["size"] = [x, 60], [width, height]
            top = max(top, 60 + height + GAP)
    positions = {
        SOURCE_INPUT_ID: (40, top, INPUT_WIDTH, 310),
        GENERATION_ID: (model_x, top, MODEL_WIDTH, model_height(example, model)),
        SAVE_VIDEO_ID: (output_x, top, OUTPUT_WIDTH, 310),
        EXTRA_INPUT_ID: (40, top + 310 + GAP, INPUT_WIDTH, 310),
        SAVE_AUDIO_ID: (output_x, top + 310 + GAP, OUTPUT_WIDTH, 130),
    }
    if example.plan in {"shots", "prompts"}:
        positions[FIRST_STEP_ID] = (40, top, INPUT_WIDTH, 240)
        positions[SECOND_STEP_ID] = (40, top + 340, INPUT_WIDTH, 240)
        if "image" in example.sources:
            positions[SOURCE_INPUT_ID] = (model_x, top + model_height(example, model) + GAP, MODEL_WIDTH, 310)
    elif ("ending_image" in example.sources) and "image" not in example.sources:
        positions[EXTRA_INPUT_ID] = (40, top, INPUT_WIDTH, 310)
    for number, (x, y, width, height) in positions.items():
        if number in by_id:
            by_id[number]["pos"], by_id[number]["size"] = [x, y], [width, height]
    return link_routes(example, positions)


def link_routes(example: Example, positions: dict[int, tuple[int, int, int, int]]) -> dict[str, Json]:
    """Route sequence and image links around the node columns without changing their endpoints."""
    model_x, top = positions[GENERATION_ID][:2]
    output_x = positions[SAVE_VIDEO_ID][0]
    extra: dict[str, Json] = {"ds": {"scale": 0.6, "offset": [160, 200]}}
    if example.plan in {"shots", "prompts"}:
        link_id = 3 if (example.plan == "prompts") and ("image" in example.sources) else 2
        reroutes: list[Json] = [
            {"id": 1, "pos": [470, top + 40], "linkIds": [link_id]},
            {"id": 2, "parentId": 1, "pos": [470, top + 270], "linkIds": [link_id]},
            {"id": 3, "parentId": 2, "pos": [10, top + 270], "linkIds": [link_id]},
        ]
        extensions: list[Json] = [{"id": link_id, "parentId": 3}]
        if "image" in example.sources:
            image_y = positions[SOURCE_INPUT_ID][1]
            reroutes.extend(
                [
                    {"id": 4, "pos": [output_x - 20, image_y + 40], "linkIds": [2]},
                    {"id": 5, "parentId": 4, "pos": [output_x - 20, top - 60], "linkIds": [2]},
                    {"id": 6, "parentId": 5, "pos": [model_x - 20, top - 60], "linkIds": [2]},
                    {"id": 7, "parentId": 6, "pos": [model_x - 20, top + 15], "linkIds": [2]},
                ]
            )
            extensions.append({"id": 2, "parentId": 7})
        extra.update(reroutes=reroutes, linkExtensions=extensions)
    return extra
