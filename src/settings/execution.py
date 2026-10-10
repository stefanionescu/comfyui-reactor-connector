"""Identify effective execution changes without exposing a secret-derived value."""

import secrets
from ..state.credentials import Credential
from ..state.settings import Settings, ExecutionConfiguration


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
        """Return settings and credentials with a cache token renewed when execution inputs change."""
        previous = self._previous
        generation = previous.generation if previous is not None else secrets.token_hex(16)
        if previous is not None and (previous.credential != credential or previous.settings != settings):
            generation = secrets.token_hex(16)
        current = ExecutionConfiguration(settings, credential, generation)
        self._previous = current
        return current
