# Python typing

Read this rule when you write Python type annotations.

## Annotations

A variable annotation appears where the compiler cannot infer a clear type, such as an empty collection, not on every
intermediate value.

## Any, object, and shapes

Use `object` for a value of any type when the function only uses operations every object has, such as passing it to
`str()`. Also use it for an ignored callback result. Reserve `Any` for what the type system cannot express, a correct
annotation that makes the API unreasonable, or a value that escapes checking on purpose. Never use it as a shortcut; a
protocol, type variable, overload, or small value object models the contract first.

Arguments take protocols and abstract collections from `collections.abc`, such as `Iterable`, `Sequence`, `Mapping`, or
`Callable`, and `object` for any value. Implementations return concrete types such as `list`, `dict`, or a dataclass.
Protocols and abstract base classes choose return types by the promised interface. A union return that forces callers
into an immediate `isinstance()` branch becomes separate functions, a tagged dataclass, a protocol, or a small hierarchy
with a common contract.

## Type variables and forward references

### Type variable naming

A private unconstrained type variable can use `_T` or `_P`. A public or constrained one has a descriptive name such as
`Key`, with `_co` and `_contra` for variance, never a single-letter `T` or `P`. `ParamSpec` forwards the parameters of a
callable. Give a `Callable` the signature its consumer needs; do not leave it bare.

### Forward references

`from __future__ import annotations` handles forward references and stays as the project's convention even where newer
Python defers evaluation. Quote a type only where the runtime does not provide future annotations or a
type-checking-only import needs it. Use a `TYPE_CHECKING` import only when the runtime does not need the symbol.
Validators and frameworks that evaluate annotations need the real import. A type-only circular import signals a need to
move the shared contract.

## Protocols

Define a structural interface with a narrow `typing.Protocol` near the consumer, holding only what it needs.
Implementations satisfy it without importing or subclassing it. `@runtime_checkable` exists only for a real
`isinstance()` need. An abstract base class serves nominal identity, runtime instantiation checks, or a standard-library
contract, never shared implementation mixed with interface definition.
