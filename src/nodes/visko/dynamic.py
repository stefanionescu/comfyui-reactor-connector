"""Generate Visko Dynamic video with synchronized audio."""

from typing import ClassVar
from .stable import ViskoStableGenerate
from ...execution.visko.operation import ViskoStableOperation, ViskoDynamicOperation


class ViskoDynamicGenerate(ViskoStableGenerate):
    """Use the Dynamic deployment with its own stable public node ID."""

    node_id: ClassVar[str] = "ReactorIncViskoDynamicGenerate"
    display_name: ClassVar[str] = "Visko Dynamic: Generate Video (Reactor)"
    operation_type: ClassVar[type[ViskoStableOperation]] = ViskoDynamicOperation
