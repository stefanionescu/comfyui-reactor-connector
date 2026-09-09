"""Generate Visko Dynamic video with synchronized audio."""

from typing import ClassVar
from .stable import ViskoStableGenerate
from ...execution.visko.request import ViskoStableRequest, ViskoDynamicRequest


class ViskoDynamicGenerate(ViskoStableGenerate):
    """Use the Dynamic deployment with its own stable public node ID."""

    node_id: ClassVar[str] = "ReactorIncViskoDynamicGenerate"
    request_type: ClassVar[type[ViskoStableRequest]] = ViskoDynamicRequest
