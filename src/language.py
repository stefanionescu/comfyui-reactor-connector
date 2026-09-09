"""Read bundled translation text without changing model or workflow identifiers."""

from __future__ import annotations

import re
import json
from pathlib import Path
from functools import cache
from contextvars import ContextVar
from contextlib import contextmanager
from ..config.security import LANGUAGE_PATTERN
from typing import cast, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator

_language = ContextVar("reactor_language", default="en")

type MessageFile = Literal["nodeDefs", "main", "commands", "workflows", "prompts"]


@cache
def available_languages() -> frozenset[str]:
    """List the language folders installed with the package."""
    root = Path(__file__).resolve().parents[1] / "locales"
    return frozenset(
        path.name for path in root.iterdir() if path.is_dir() and re.fullmatch(LANGUAGE_PATTERN, path.name)
    )


@cache
def read_messages(name: MessageFile, language: str = "en") -> dict[str, object]:
    """Read a checked package resource once; callers leave its contents unchanged."""
    path = Path(__file__).resolve().parents[1] / "locales" / language / f"{name}.json"
    if language != "en" and not path.is_file():
        return {}
    return cast("dict[str, object]", json.loads(path.read_text(encoding="utf-8")))


def translate(name: MessageFile, key: str, **values: str | int | float) -> str:
    """Read a message in the current request language, with an English fallback."""
    messages = read_messages(name)
    localized = read_messages(name, _language.get())
    if name == "main":
        messages = cast("dict[str, object]", messages["reactorInc"])
        localized = cast("dict[str, object]", localized.get("reactorInc", {}))
    message = localized.get(key, messages[key])
    if not isinstance(message, str):
        raise TypeError(key)
    return message.format_map(values) if values else message


@contextmanager
def language_scope(language: str) -> Generator[None, None, None]:
    """Select a safe locale for one request or build and restore it when finished."""
    candidates = locale_candidates(language)
    languages = {name.lower(): name for name in available_languages()}
    selected = next((languages[name] for name in candidates if name in languages), "en")
    token = _language.set(selected)
    try:
        yield
    finally:
        _language.reset(token)


def locale_candidates(language: str) -> list[str]:
    """Prefer exact and language-level resources while keeping Chinese writing systems distinct."""
    exact = language.split(",", 1)[0].split(";", 1)[0].strip().replace("_", "-").lower()
    traditional = any(exact == tag or exact.startswith(tag + "-") for tag in ("zh-tw", "zh-hk", "zh-mo", "zh-hant"))
    base = "zh-tw" if traditional else exact.split("-", 1)[0]
    return list(dict.fromkeys((exact, base, "en")))
