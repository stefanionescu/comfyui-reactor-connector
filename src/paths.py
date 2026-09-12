"""Resolve resources belonging to the installed extension."""

from pathlib import Path


EXTENSION_ROOT = Path(__file__).resolve().parents[1]


__all__ = ["EXTENSION_ROOT"]
