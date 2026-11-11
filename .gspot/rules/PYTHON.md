# Python

Read this rule when you change Python code.

## Python scope

Importing a module does no I/O, starts no work, and parses no arguments. A new package puts its code under `src/`.

## Environment and settings

An importable module never depends on an active shell, a virtual environment, the current folder, or a globally
installed package. Imports resolve through project configuration, editable installs, `python -m`, or the configured
environment.

## Imports

Break an import cycle by moving shared data or interfaces into a lower-level module.

## Docstrings

Write docstrings in the style that `python.docstring_convention` names; Ruff and pydoclint both check it. Each docstring
matches its signature and behavior. When the setting is unset, use the style the file already uses, or Google style in a
new file. pydoclint checks Google and NumPy styles.

## Constants, globals, and mutable state

Do not expose mutable global state or lazy singletons as public API. No ordinary call changes a module global as a
hidden side effect.

## Main programs

An executable module puts its behavior in `main()`, runs it under the `__main__` guard, and prefers
`raise SystemExit(main())` when `main()` returns an exit code. Repository entry points run as
`python -m package.module`, and shell scripts call Python modules rather than inline snippets.

## Functions

Do not hide I/O in a helper that looks like a pure transformation. Declare an ordinary no-result case in the signature
and return an explicit `None`. Input that violates the API contract raises a specific exception.

## Classes

Write a class only for real state, invariants, or behavior. Do not turn a coordinating function without polymorphism
into a class. Never group static functions into a class.

Keep `__init__` small: it takes the values the class needs rather than the external objects that carry them, and
validates invariants. Keep it separate from database rows, object-relational mapping (ORM) objects, API payloads, CLI
namespaces, or provider responses. An external representation enters through a classmethod named constructor such as
`decode_row` or `parse_payload` when the class owns that conversion. Neither `ClassName(**external_attributes)` nor a
constructor that only renames the initializer handles that conversion.

Keep loading, serialization, and validation systems outside the business object. Keep a derived attribute cheap and
deterministic. Build it from initialized fields; a named constructor handles derivation through I/O or complex parsing.

Do not put variants in one class with a type field and optional attributes that apply to some values.

## Exception contracts

A custom exception inherits from `Exception`, describes its condition in the docstring, and lives beside the behavior
that raises it rather than in a one-declaration file.

## Boolean logic and comparisons

Use truth-value testing only when all falsy values mean the same thing. Do not treat an empty collection, zero, and a
missing value as interchangeable by default.

## Files and stateful resources

A generator can keep a resource open while suspended. Make that lifetime clear to callers, especially when they can stop
consuming it early.

For large inputs, provide an explicit streaming interface whose caller owns the open resource or uses a context manager.
Do not materialize the full input only to avoid documenting its lifetime.

Write to a temporary file in the same folder, validate it, then rename it over the target. Clean up only paths and
resources owned by the current operation.

## Naming

### Python types and dataclasses

- Give `Path` variables names that reveal whether they point to a folder, file, report, output, or repository root.
- Use `*_path` for filesystem paths and `*_folder` only for folders.
- Use `*_id` only for real identifiers. Never use it for arbitrary names or labels.
- Use `*_name` for display or provider names.
- Use `*_key` for dictionary and supported variant keys.
