from collections.abc import Sequence

class Input: ...
class Output: ...
class ComfyNode: ...

class NodeOutput:
    def __init__(self, *outputs: object, ui: dict[str, object] | None = None) -> None: ...

class Widget(Input):
    def __init__(
        self,
        id: str,
        *,
        display_name: str = ...,
        advanced: bool = ...,
        default: object = ...,
        min: int | float = ...,
        max: int | float = ...,
        step: int | float = ...,
        tooltip: str = ...,
        multiline: bool = ...,
        placeholder: str = ...,
        control_after_generate: bool = ...,
        optional: bool = ...,
    ) -> None: ...

class OutputWidget(Output):
    def __init__(self, *, display_name: str = ...) -> None: ...

class String:
    Input = Widget
    Output = OutputWidget

class Float:
    Input = Widget

class Int:
    Input = Widget

class Boolean:
    Input = Widget

class Image:
    Input = Widget

class Combo:
    class Input(Widget):
        def __init__(
            self,
            id: str,
            *,
            options: list[str],
            display_name: str = ...,
            default: str = ...,
            tooltip: str = ...,
        ) -> None: ...

class Video:
    Input = Widget
    Output = OutputWidget

class Audio:
    Output = OutputWidget

class Schema:
    node_id: str
    def __init__(
        self,
        node_id: str,
        *,
        display_name: str = ...,
        category: str = ...,
        inputs: Sequence[Input] = ...,
        outputs: Sequence[Output] = ...,
        description: str = ...,
        search_aliases: Sequence[str] = ...,
        is_experimental: bool = ...,
    ) -> None: ...
