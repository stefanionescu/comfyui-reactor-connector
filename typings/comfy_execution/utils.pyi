from typing import NamedTuple

class ExecutionContext(NamedTuple):
    prompt_id: str
    node_id: str
    list_index: int | None

def get_executing_context() -> ExecutionContext | None: ...
