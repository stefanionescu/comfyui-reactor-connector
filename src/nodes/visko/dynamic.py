"""Expose each Visko deployment with native synchronized video and audio outputs."""

from typing import ClassVar
from .stable import ViskoStableGenerate
from ...execution.visko import ViskoStableRequest, ViskoDynamicRequest


class ViskoDynamicGenerate(ViskoStableGenerate):
    """Use the Dynamic deployment with its own stable public node ID."""

    node_id: ClassVar[str] = "ReactorIncViskoDynamicGenerate"
    display_name: ClassVar[str] = "Reactor Visko Dynamic: Generate video"
    request_type: ClassVar[type[ViskoStableRequest]] = ViskoDynamicRequest
