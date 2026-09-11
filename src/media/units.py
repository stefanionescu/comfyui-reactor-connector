"""Convert configured media size units at runtime boundaries."""

_BYTES_PER_MEBIBYTE = 1_048_576


def convert_mebibytes_to_bytes(mebibytes: int) -> int:
    """Return bytes for a configured size measured in mebibytes."""
    return mebibytes * _BYTES_PER_MEBIBYTE


__all__ = ["convert_mebibytes_to_bytes"]
