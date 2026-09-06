"""Identify an execution without copying private inputs into its output."""

import re
import tomllib
from dataclasses import dataclass
from functools import lru_cache
from importlib.metadata import version
from pathlib import Path
from typing import Self
from uuid import uuid4

from ..errors import ConnectorError, ErrorCode
from ..json_data import Json, object_value, parse_json
from ..node_catalog import NODE_MODELS


@lru_cache(maxsize=1)
def connector_version() -> str:
    """Read the package's single version source before a paid connection starts."""
    path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    try:
        if path.stat().st_size > 65_536:
            raise ValueError
        with path.open("rb") as file:
            value: object = tomllib.load(file)["project"]["version"]
        if type(value) is not str or not 1 <= len(value) <= 80:
            raise ValueError
        return value
    except (OSError, ValueError, KeyError, TypeError):
        raise ConnectorError(
            ErrorCode.CONFIGURATION, "The connector's version is missing. Reinstall the package."
        ) from None


@lru_cache(maxsize=1)
def package_identity() -> str | None:
    """Identify a built package; a plain source checkout has no package manifest."""
    path = Path(__file__).resolve().parents[2] / ".reactor-package.json"
    try:
        with path.open("rb") as file:
            encoded = file.read(1_048_577)
    except FileNotFoundError:
        return None
    except OSError:
        raise ConnectorError(
            ErrorCode.CONFIGURATION, "The package identity could not be read. Reinstall it."
        ) from None
    data = object_value(parse_json(encoded.decode(), max_bytes=1_048_576, max_depth=4))
    identity = data.get("identity")
    if not isinstance(identity, str) or re.fullmatch(r"[a-f0-9]{64}", identity) is None:
        raise ConnectorError(
            ErrorCode.CONFIGURATION, "The package identity is invalid. Reinstall the package."
        )
    return identity


@dataclass(frozen=True, slots=True)
class RunReport:
    run_id: str
    node_id: str
    model_name: str
    requested_duration_seconds: float
    connector_version: str
    sdk_version: str
    package_identity: str | None

    @classmethod
    def prepare(cls, node_id: str, model_name: str, duration_seconds: float) -> Self:
        if node_id not in NODE_MODELS:
            raise ConnectorError(ErrorCode.CONFIGURATION, "The Reactor node is not registered.")
        return cls(
            uuid4().hex,
            node_id,
            model_name,
            duration_seconds,
            connector_version(),
            version("reactor-sdk"),
            package_identity(),
        )

    def to_json(self) -> dict[str, Json]:
        return {
            "schema_version": 1,
            "run_id": self.run_id,
            "node_id": self.node_id,
            "model_name": self.model_name,
            "requested_duration_seconds": self.requested_duration_seconds,
            "connector_version": self.connector_version,
            "sdk_version": self.sdk_version,
            "package_identity": self.package_identity,
        }
