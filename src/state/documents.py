"""JSON values exchanged with browsers, providers, and private storage."""

type Json = bool | int | float | str | list[Json] | dict[str, Json] | None
