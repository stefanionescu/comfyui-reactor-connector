"""Admission records shared by the session queue and its callers."""

import asyncio
from dataclasses import dataclass


@dataclass(eq=False, slots=True)
class AdmissionTicket:
    """A wake-up event owned only by the loop that requested admission."""

    loop: asyncio.AbstractEventLoop
    changed: asyncio.Event


__all__ = ["AdmissionTicket"]
