"""Place each example's instructions, controls, and previews in reading order."""

import math
import re
import textwrap

from reactor_comfy.json_data import Json

from .workflow_definitions import Example

GAP = 60
INPUT_WIDTH = 400
MODEL_WIDTH = 440
OUTPUT_WIDTH = 360


def note_height(text: str, width: int) -> int:
    """Allow for the native note's font, wrapped lines, and paragraph margins."""
    height = 20
    for paragraph in text.split("\n\n"):
        plain = re.sub(r"[*`#]", "", paragraph)
        lines = sum(
            max(1, len(textwrap.wrap(line, int((width - 32) / 5.5)))) for line in plain.splitlines()
        )
        height += lines * 14 + 10
    return math.ceil(height / 20) * 20


def model_height(example: Example) -> int:
    """Reserve prompt space and the controls used by this model."""
    if example.clip_count > 1:
        return 460
    if example.model.startswith("visko"):
        return 470
    if example.model == "ltx2":
        return 410
    if example.model.startswith("lingbot"):
        return 420
    if example.model == "x2" and not example.webcam:
        return 360
    return 330


def arrange(nodes: list[Json], example: Example) -> dict[str, Json]:
    """Align columns while keeping each note and node sized for its content."""
    records = [item for item in nodes if isinstance(item, dict)]
    by_id = {item["id"]: item for item in records if isinstance(item["id"], int)}
    has_inputs = any(number in by_id for number in (2, 5, 6))
    model_x = 40 + INPUT_WIDTH + GAP if has_inputs else 40
    output_x = model_x + MODEL_WIDTH + GAP
    first_width = INPUT_WIDTH if has_inputs else MODEL_WIDTH
    top = 60
    for number, x, width in (
        (1, 40, first_width),
        (8, model_x if has_inputs else output_x, MODEL_WIDTH if has_inputs else OUTPUT_WIDTH),
    ):
        if number not in by_id:
            continue
        note = by_id[number]
        widgets = note["widgets_values"]
        if isinstance(widgets, list) and isinstance(widgets[0], str):
            height = note_height(widgets[0], width)
            note["pos"], note["size"] = [x, 60], [width, height]
            top = max(top, 60 + height + GAP)
    positions = {
        2: (40, top, INPUT_WIDTH, 310),
        3: (model_x, top, MODEL_WIDTH, model_height(example)),
        4: (output_x, top, OUTPUT_WIDTH, 310),
        5: (40, top + 310 + GAP, INPUT_WIDTH, 310),
        7: (output_x, top + 310 + GAP, OUTPUT_WIDTH, 130),
    }
    if example.storyboard or example.prompt_sequence:
        positions[5] = (40, top, INPUT_WIDTH, 240)
        positions[6] = (40, top + 340, INPUT_WIDTH, 240)
        if example.image:
            positions[2] = (model_x, top + model_height(example) + GAP, MODEL_WIDTH, 310)
    elif example.ending_image and not example.image:
        positions[5] = (40, top, INPUT_WIDTH, 310)
    for number, (x, y, width, height) in positions.items():
        if number in by_id:
            by_id[number]["pos"], by_id[number]["size"] = [x, y], [width, height]
    extra: dict[str, Json] = {"ds": {"scale": 0.6, "offset": [20, 20]}}
    if example.storyboard or example.prompt_sequence:
        link_id = 3 if example.prompt_sequence and example.image else 2
        reroutes: list[Json] = [
            {"id": 1, "pos": [470, top + 40], "linkIds": [link_id]},
            {"id": 2, "parentId": 1, "pos": [470, top + 270], "linkIds": [link_id]},
            {"id": 3, "parentId": 2, "pos": [10, top + 270], "linkIds": [link_id]},
        ]
        extensions: list[Json] = [{"id": link_id, "parentId": 3}]
        if example.image:
            image_y = positions[2][1]
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
