"""Identify an execution without copying private inputs into its output."""

import tomllib
from uuid import uuid4
from functools import lru_cache
from ..language import translate
from ..paths import EXTENSION_ROOT
from ..state.reports import RunReport
from importlib.metadata import version
from ..errors import ErrorCode, ConnectorError
from ...config.package import MAX_PROJECT_FILE_BYTES, MAX_VERSION_CHARACTERS


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
    path = EXTENSION_ROOT / "pyproject.toml"
    invalid = ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.packageVersionMissing"))
    try:
        if path.stat().st_size > MAX_PROJECT_FILE_BYTES:
            raise invalid
        with path.open("rb") as file:
            value: object = tomllib.load(file)["project"]["version"]
        if type(value) is not str or not 1 <= len(value) <= MAX_VERSION_CHARACTERS:
            raise invalid
    except (OSError, ValueError, KeyError, TypeError):
        raise invalid from None
    else:
        return value


__all__ = ["connector_version", "prepare_report"]
