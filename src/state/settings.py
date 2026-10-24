"""Execution settings and private configuration snapshot records."""

from dataclasses import field, dataclass

from .credentials import Credential


@dataclass(frozen=True, slots=True)
class Settings:
    """Host limits that a workflow cannot increase.

    Attributes:
        max_session_seconds: Maximum remote session lifetime.
        max_upload_megabytes: Maximum source upload size.

    """

    max_session_seconds: int
    max_upload_megabytes: int


@dataclass(frozen=True, slots=True)
class ExecutionConfiguration:
    """One private settings and credential snapshot for one operation.

    Attributes:
        settings: Effective execution limits and preferences.
        credential: Private provider credential excluded from representations.
        generation: Token identifying the effective execution configuration.

    """

    settings: Settings
    credential: Credential = field(repr=False)
    generation: str
