"""Private credential values with redacted representations."""

from dataclasses import field, dataclass


@dataclass(frozen=True, slots=True)
class Credential:
    """A secret that only the provider boundary reads.

    Attributes:
        value: Validated secret excluded from representations.

    """

    value: str = field(repr=False)


@dataclass(frozen=True, slots=True)
class SessionToken:
    """A private token with a provider expiry validated before construction.

    Attributes:
        value: Session authorization token excluded from representations.

    """

    value: str = field(repr=False)
