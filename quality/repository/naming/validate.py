"""Data-driven name validation."""

from __future__ import annotations

from typing import TYPE_CHECKING
from quality.repository.naming.cases import matches_case
from quality.repository.naming.parts import identifier_parts

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping


def validate_name(name: str, cases: Iterable[str], policy: Mapping[str, object]) -> list[str]:
    """Return policy diagnostics for one name."""
    diagnostics: list[str] = []
    words = identifier_parts(name)
    if cases and not any(matches_case(name, case_name) for case_name in cases):
        diagnostics.append(f'uses invalid case for "{name}"')
    max_characters = policy.get("max_characters")
    if isinstance(max_characters, int) and len(name) > max_characters:
        diagnostics.append(f"has {len(name)} characters over limit {max_characters}")
    max_words = policy.get("max_words")
    if isinstance(max_words, int) and len(words) > max_words:
        diagnostics.append(f"has {len(words)} words over limit {max_words}")
    if len(words) != len(set(words)):
        diagnostics.append("contains duplicate words")
    return diagnostics
