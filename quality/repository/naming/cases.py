"""Identifier case checks."""

from __future__ import annotations

import re

SNAKE_RE = re.compile(r"^_?[a-z][a-z0-9_]*_?$|^__[a-z0-9_]+__$")
UPPER_SNAKE_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PASCAL_RE = re.compile(r"^[A-Z][A-Za-z0-9]*$")
CASE_PATTERNS = {
    "snake": SNAKE_RE,
    "upper-snake": UPPER_SNAKE_RE,
    "kebab": KEBAB_RE,
    "pascal": PASCAL_RE,
}


def matches_case(name: str, case_name: str) -> bool:
    """Return whether a name matches a configured case."""
    pattern = CASE_PATTERNS.get(case_name)
    if pattern is None:
        return False
    return bool(pattern.match(name))
