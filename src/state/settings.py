"""Execution settings and private configuration snapshot records."""

from .documents import Json
from .credentials import Credential
from dataclasses import field, asdict, dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    """Host limits that a workflow cannot increase.

    Attributes:
        max_session_seconds: Maximum remote session lifetime.
        max_upload_megabytes: Maximum source upload size.
        catalog_auto_check: Whether public metadata checks are enabled.

    """

    max_session_seconds: int
    max_upload_megabytes: int
    catalog_auto_check: bool

    def to_json(self) -> dict[str, Json]:
        """Return only non-secret settings for the local configuration route."""
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ExecutionConfiguration:
    """One private settings and credential snapshot for an admitted operation.

    Attributes:
        settings: Effective execution limits and preferences.
        credential: Private provider credential excluded from representations.
        generation: Token identifying the effective execution configuration.

    """

    settings: Settings
    credential: Credential = field(repr=False)
    generation: str
