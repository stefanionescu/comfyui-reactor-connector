"""Identify an execution without copying private inputs into its output."""

import re
import tomllib
from uuid import uuid4
from typing import Self
from pathlib import Path
from functools import lru_cache
from ..language import translate
from dataclasses import dataclass
from importlib.metadata import version
from ...config.models.nodes import NODE_MODELS
from ..errors import ErrorCode, ConnectorError
from ..serialization import Json, parse_json, mapping_value
from ...config.package import (
    MAX_MANIFEST_BYTES,
    MAX_MANIFEST_DEPTH,
    MAX_PROJECT_FILE_BYTES,
    MAX_VERSION_CHARACTERS,
    PACKAGE_IDENTITY_PATTERN,
)


@dataclass(frozen=True, slots=True)
class RunReport:
    """Public recording facts that identify the model and connector versions."""

    run_id: str
    node_id: str
    model_name: str
    requested_duration_seconds: float
    connector_version: str
    sdk_version: str
    package_identity: str | None

    @classmethod
    def prepare(cls, node_id: str, model_name: str, duration_seconds: float) -> Self:
        """Identify a registered node run and its installed connector and SDK versions."""
        if node_id not in NODE_MODELS:
            raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.nodeUnregistered"))
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
        """Serialize public recording facts without prompts, credentials, or media inputs."""
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


@lru_cache(maxsize=1)
def connector_version() -> str:
    """Read the package's single version source before a paid connection starts."""
    path = Path(__file__).resolve().parents[2] / "pyproject.toml"
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


@lru_cache(maxsize=1)
def package_identity() -> str | None:
    """Identify a built package; a plain source checkout has no package manifest."""
    path = Path(__file__).resolve().parents[2] / ".reactor-package.json"
    try:
        with path.open("rb") as file:
            encoded = file.read(MAX_MANIFEST_BYTES + 1)
    except FileNotFoundError:
        return None
    except OSError:
        raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.packageIdentityUnreadable")) from None
    payload = mapping_value(parse_json(encoded.decode(), max_bytes=MAX_MANIFEST_BYTES, max_depth=MAX_MANIFEST_DEPTH))
    identity = payload.get("identity")
    if not isinstance(identity, str) or re.fullmatch(PACKAGE_IDENTITY_PATTERN, identity) is None:
        raise ConnectorError(ErrorCode.CONFIGURATION, translate("main", "errors.packageIdentityInvalid"))
    return identity
