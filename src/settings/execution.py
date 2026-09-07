"""Identify effective execution changes without exposing a secret-derived value."""

import secrets
from .settings import Settings
from ..credentials import Credential
from dataclasses import field, dataclass


@dataclass(frozen=True, slots=True)
class ExecutionConfiguration:
    """One private settings and credential snapshot for an admitted operation."""

    settings: Settings
    credential: Credential = field(repr=False)
    generation: str


class ConfigurationGeneration:
    """Compare private values under the configuration store's lock."""

    def __init__(self) -> None:
        """Start without a reusable execution snapshot."""
        self._previous: ExecutionConfiguration | None = None

    def invalidate(self) -> None:
        """Prevent reuse after a key is removed or configuration cannot be read."""
        self._previous = None

    def credential_saved(self, credential: Credential) -> None:
        """Keep a no-op key save from causing another billed execution."""
        if self._previous is not None and self._previous.credential != credential:
            self.invalidate()

    def snapshot(self, settings: Settings, credential: Credential) -> ExecutionConfiguration:
        """Return a random token, independent of key bytes and account identifiers."""
        previous = self._previous
        generation = previous.generation if previous is not None else secrets.token_hex(16)
        if previous is not None and (
            previous.credential != credential or execution_settings(previous.settings) != execution_settings(settings)
        ):
            generation = secrets.token_hex(16)
        current = ExecutionConfiguration(settings, credential, generation)
        self._previous = current
        return current


def execution_settings(settings: Settings) -> dict[str, object]:
    """Exclude catalog check preferences that cannot change generated media."""
    return {
        key: value
        for key, value in settings.to_json().items()
        if key not in {"catalog_auto_check", "catalog_interval_hours"}
    }
