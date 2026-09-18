"""Identify an execution without copying private inputs into its output."""

import tomllib
from uuid import uuid4
from functools import lru_cache
from ..paths import EXTENSION_ROOT
from ..state.reports import RunReport
from importlib.metadata import version
from ..errors import ErrorCode, ConnectorError
from ..config.messages.settings import PACKAGE_VERSION_MISSING


def prepare_report(node_id: str, model_name: str, duration_seconds: float) -> RunReport:
    """Identify a registered node run and its installed connector and SDK versions."""
    return RunReport(
        uuid4().hex,
        node_id,
        model_name,
        duration_seconds,
        connector_version(),
        version("reactor-sdk"),
    )


@lru_cache(maxsize=1)
def connector_version() -> str:
    """Read the package's single version source before a connection starts."""
    invalid = ConnectorError(ErrorCode.CONFIGURATION, PACKAGE_VERSION_MISSING)
    try:
        with (EXTENSION_ROOT / "pyproject.toml").open("rb") as file:
            value: object = tomllib.load(file)["project"]["version"]
    except (OSError, ValueError, KeyError, TypeError):
        raise invalid from None
    if not isinstance(value, str) or not value:
        raise invalid
    return value


__all__ = ["connector_version", "prepare_report"]
