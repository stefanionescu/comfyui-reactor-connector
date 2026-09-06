"""Read header facts from a completed connector MP4 in a terminable process."""

import json
import sys
from pathlib import Path

import av


def describe(path: Path, maximum_bytes: int) -> dict[str, int | bool | None]:
    """Use the saved video stream's clock; never infer duration from frame count."""
    size = path.stat().st_size
    if not 0 < size <= maximum_bytes:
        raise ValueError
    with (
        path.open("rb") as file,
        av.open(file, mode="r", format="mp4", options={"protocol_whitelist": "pipe"}) as reader,
    ):
        if len(reader.streams.video) != 1 or len(reader.streams.audio) > 1:
            raise ValueError
        stream = reader.streams.video[0]
        width, height = stream.codec_context.width, stream.codec_context.height
        if not 2 <= width <= 8192 or not 2 <= height <= 8192:
            raise ValueError
        duration_us = None
        if stream.duration is not None and stream.time_base is not None:
            duration_us = round(stream.duration * stream.time_base * 1_000_000)
            if not 0 < duration_us <= 3_601_000_000:
                raise ValueError
        return {
            "width": width,
            "height": height,
            "duration_us": duration_us,
            "file_bytes": size,
            "has_audio": bool(reader.streams.audio),
        }


def main() -> int:
    print(json.dumps({"ready": True}), flush=True)
    try:
        if len(sys.argv) != 3:
            raise ValueError
        result = describe(Path(sys.argv[1]), int(sys.argv[2]))
    except Exception:
        print(json.dumps({"error": "recording_details"}), flush=True)
        return 1
    print(json.dumps(result), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
