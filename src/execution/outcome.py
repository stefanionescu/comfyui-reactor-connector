"""Track termination separately from capture success and local cleanup."""

from dataclasses import dataclass
from .diagnostics import FailureReport


@dataclass(slots=True)
class SessionOutcome:
    """Facts used by the host to decide whether another session may start."""

    connection_attempted: bool = False
    termination_confirmed: bool = False
    diagnostic: FailureReport | None = None

    @property
    def termination_uncertain(self) -> bool:
        """Report whether a connection was attempted without confirmed termination."""
        return self.connection_attempted and not self.termination_confirmed
