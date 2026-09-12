"""Private credential values with redacted representations."""

from dataclasses import field, dataclass


@dataclass(frozen=True, slots=True, repr=False)
class Credential:
    """A secret revealed explicitly at the provider boundary.

    Attributes:
        _value: Validated secret excluded from representations.

    """

    _value: str = field(repr=False)

    def __repr__(self) -> str:
        """Identify the credential type without revealing its value."""
        return "Credential(<redacted>)"

    def __str__(self) -> str:
        """Return a redacted label instead of the credential value."""
        return "<redacted>"

    def reveal(self) -> str:
        """Return the secret only for an authorized private provider request."""
        return self._value


@dataclass(frozen=True, slots=True, repr=False)
class SessionToken:
    """A private token with a provider expiry validated before construction.

    Attributes:
        value: Session authorization token excluded from representations.

    """

    value: str = field(repr=False)

    def __repr__(self) -> str:
        """Hide the token from object representations."""
        return "SessionToken(<redacted>)"

    def __str__(self) -> str:
        """Hide the token from formatted text."""
        return "<redacted>"


__all__ = ["Credential", "SessionToken"]
