# Working on Python

These rules apply to connector source, media workers, local quality tools,
build scripts, generated Python examples, and committed Python snippets.

Use this file together with [`GENERAL.md`](GENERAL.md), [`NAMING.md`](NAMING.md),
and the local tooling configured in `pyproject.toml` and `quality/`.

## Contents

- [Core Python philosophy](#core-python-philosophy)
- [Source material decisions](#source-material-decisions)
- [Local tooling authority](#local-tooling-authority)
- [Runtime, encoding, and files](#runtime-encoding-and-files)
- [Environment and configuration](#environment-and-configuration)
- [Package installation security](#package-installation-security)
- [Module structure](#module-structure)
- [Imports](#imports)
- [Public and internal interfaces](#public-and-internal-interfaces)
- [Formatting](#formatting)
- [Naming](#naming)
- [Comments and docstrings](#comments-and-docstrings)
- [Type annotations](#type-annotations)
- [Constants, globals, and mutable state](#constants-globals-and-mutable-state)
- [Functions and methods](#functions-and-methods)
- [Classes](#classes)
- [Exceptions and error handling](#exceptions-and-error-handling)
- [Assertions](#assertions)
- [Boolean logic and comparisons](#boolean-logic-and-comparisons)
- [Control flow simplification](#control-flow-simplification)
- [Iteration and collections](#iteration-and-collections)
- [Strings, logging, and error messages](#strings-logging-and-error-messages)
- [Files and stateful resources](#files-and-stateful-resources)
- [Main programs and top-level code](#main-programs-and-top-level-code)
- [Packages and architecture](#packages-and-architecture)
- [Power features](#power-features)
- [Threading and concurrency](#threading-and-concurrency)
- [Manual verification](#manual-verification)
- [Verification commands](#verification-commands)
- [Review checklist](#review-checklist)
- [Anti-patterns](#anti-patterns)
- [ComfyUI and Reactor boundaries](#comfyui-and-reactor-boundaries)

## Core Python philosophy

Rules:

- Write readable Python before clever Python.
- Prefer explicit data flow, clear names, and small functions.
- Keep code import-stable. Importing a module must not load models, initialize
  engines, touch external services, start background work, parse CLI arguments, or mutate
  runtime state.
- Prefer project-specific rules over generic style guides when they conflict.
- Prefer consistency with the surrounding module when a source guide allows more
  than one style.
- Do not make style-only churn outside the requested scope.
- Do not preserve obsolete Python APIs, wrappers, re-exports, or alternate code
  paths. Follow [`GENERAL.md`](GENERAL.md) for replacement work.
- Make public behavior clear through names, type annotations, docstrings, and
  manual verification when runtime behavior changes.
- Use exceptions for exceptional conditions, not for ordinary branch logic.
- Use built-in language features directly when they express the operation
  clearly.

Good Python is easy to scan:

```python
"""Yield request text from chat messages."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PromptMessage:
    """One request message."""

    content: str


def iter_message_text(messages: Iterable[PromptMessage]) -> Iterable[str]:
    """Yield text content from request messages."""
    for message in messages:
        yield message.content


__all__ = [
    "PromptMessage",
    "iter_message_text",
]
```

Bad Python hides behavior and ownership:

```python
from examples import *

STATE = {"instance": None}


def get_instance():
    import importlib

    return importlib.import_module("loader").build_examples()
```

## Source material decisions

These rules adapt PEP 8, PEP 257, and the Google Python Style Guide into one
local standard for this repository.

| Topic                        | Local decision                                                                                                                                                                                                           |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Style authority              | Project rules and local tooling win over generic source guides.                                                                                                                                                          |
| Formatter line length        | Ruff is configured with `line-length = 120`; use that local limit for Python code.                                                                                                                                       |
| Standard-library line length | PEP 8's 79-character code limit and 72-character comment/docstring limit describe the Python standard library, not this repo.                                                                                            |
| Google line length           | Google's 80-character default is useful guidance for docstring summaries and comments, but local Ruff formatting is authoritative.                                                                                       |
| Formatter                    | Ruff format is the local formatter. Do not hand-format against a different style.                                                                                                                                        |
| Linter                       | Ruff lint, BasedPyright, import-linter, and custom `quality/` scripts are local policy. Pylint guidance from Google maps to these local tools.                                                                           |
| Runtime                      | The project requires Python 3.12. Use Python 3.12 syntax when it improves clarity.                                                                                                                                       |
| Future imports               | Prefer `from __future__ import annotations` in Python modules.                                                                                                                                                           |
| Quotes                       | Ruff format uses double quotes. Use double quotes for ordinary strings unless another quote avoids escaping. Docstrings always use triple double quotes.                                                                 |
| Imports                      | Use absolute imports for cross-package imports. Explicit relative sibling imports are allowed inside a package when that is the local pattern.                                                                           |
| Class/function imports       | Direct imports of public classes, functions, and constants are allowed when they keep call sites readable. Import typing and `collections.abc` symbols directly.                                                         |
| `__all__`                    | Keep `__all__` at the bottom of modules. This local rule overrides PEP 8's normal module-dunder placement for `__all__`.                                                                                                 |
| Other module dunders         | Put dunders such as `__version__` after the module docstring and future imports, before ordinary imports.                                                                                                                |
| License boilerplate          | Do not invent license boilerplate. Add it only if the project defines the exact boilerplate.                                                                                                                             |
| Function length              | Custom lint limits functions to 60 counted code lines by default. Keep functions smaller when practical.                                                                                                                 |
| File length                  | Custom lint limits runtime Python files to 300 counted code lines by default, except barrel `__init__.py` files.                                                                                                         |
| Public typing                | Public APIs should be annotated. The repo does not require every private helper to be annotated, but annotations are encouraged where they clarify contracts.                                                            |
| Typing style                 | Use modern union syntax, built-in generics, `type` statements or `TypeAlias` for real type aliases, `Annotated` for typed metadata, `object` for values that can be any object, and protocols for structural interfaces. |
| Argument and return types    | Prefer abstract input types and concrete return types for concrete implementations. Avoid union return types that force caller-side type branching.                                                                      |
| Logging                      | Modules create `logging.getLogger(__name__)`; application entrypoints configure handlers and levels. Library modules do not configure handlers except `NullHandler`.                                                     |
| Project layout               | Keep importable project code under `src/`; do not patch `sys.path` to make package imports work.                                                                                                                         |
| Inheritance                  | Prefer composition for code sharing, protocols for interfaces, and subclassing only for true specialization.                                                                                                             |
| Package installs             | Deployment installs should use pinned, hashed, binary-only requirements where practical. Do not use direct setuptools install commands.                                                                                  |
| Verification                 | Run authorized static checks; never create or run automated tests.                                                                                                                                                       |

When editing an existing file, follow the surrounding style where the source
guides allow a choice. When creating new code, use the decisions in this table.

## Local tooling authority

The local Python quality stack is:

- Ruff format.
- Ruff lint.
- BasedPyright.
- import-linter.
- Custom structural linters in `quality/`.
- Naming checks described in [`NAMING.md`](NAMING.md).

Rules:

- Treat local lint failures as policy failures.
- Do not add per-file ignores, inline ignores, or broad config exceptions unless
  the user explicitly asks for a tooling change or the violation is unavoidable.
- Do not copy an existing per-file ignore into new files.
- Do not broaden an existing exception to make unrelated code pass.
- Do not disable a rule when a clear code change can satisfy it.
- Do not run verification commands unless the user asks. When asked, run only
  the requested or necessary scoped command.

Current local tooling constraints include:

- Python source under configured directories uses snake_case `.py` filenames.
- Runtime files should stay under 300 counted code lines.
- Functions and methods should stay under 60 counted code lines.
- Runtime modules must not use local imports inside function, method, or class
  bodies.
- Runtime modules must not use lazy module loading, module-level lazy export
  hooks, or dynamic imports.
- Runtime modules must not use lazy singleton patterns.
- Runtime modules must not create import cycles.
- Packages with `__init__.py` and exactly one non-init module should be flattened
  to a single module.
- Directories should not contain multiple `.py` files with the same
  underscore-delimited prefix.
- `__all__` must appear at the bottom of each module.
- Python logic must live in Python modules. Shell scripts must call it with
  `python -m`; do not embed inline Python in shell scripts.

## Runtime, encoding, and files

Rules:

- Use Python 3.12 syntax.
- Store source files as UTF-8.
- Do not add an encoding declaration unless a tool or runtime requires it.
- Use LF line endings.
- Keep identifiers ASCII-only.
- Use English words for identifiers, comments, and docstrings unless an external
  identifier must keep another language or spelling.
- Use non-ASCII characters sparingly in string data.
- Do not use byte-order marks.
- Python filenames must use `.py`.
- Python filenames must be snake_case, except `__init__.py` and `__main__.py`.
- Python filenames must not contain dashes.
- Keep modules importable by pydoc, linting tools, and type checkers.

Bad:

```text
ModelConfig.py
model-config.py
model config.py
```

Good:

```text
model_config.py
modeling.py
__main__.py
```

## Environment and configuration

Rules:

- Treat environment variables as external text input.
- Read environment variables at a configuration or application boundary, not
  throughout business logic.
- Parse and validate environment-derived values once before passing them inward.
- Store secrets in environment variables or a secret manager, never in source
  code, documentation examples, or checked-in config.
- Do not use a real-looking default for a secret. Missing required secrets
  should fail at startup or command initialization.
- Do not make importable modules depend on an active shell, virtual
  environment, current working directory, or globally installed package.
- Use project configuration, editable installs, `python -m`, or the configured
  environment to resolve imports.
- Do not commit virtual environment directories or generated package caches.

Good:

```python
@dataclass(frozen=True)
class AppConfig:
    """Runtime configuration loaded from the environment."""

    max_items: int


def load_config(environ: Mapping[str, str]) -> AppConfig:
    """Load runtime configuration from environment variables."""
    raw_max_items = environ.get("MAX_ITEMS", "100")
    return AppConfig(max_items=int(raw_max_items))
```

Bad:

```python
def list_items() -> list[Item]:
    limit = int(os.getenv("MAX_ITEMS", "100"))
    return query_items(limit=limit)
```

## Package installation security

ComfyUI owns a shared Python environment. Use its interpreter for installation.
Keep compatible runtime dependency constraints in `pyproject.toml` and generate
`requirements.txt` from them. Do not replace the host's Torch or other host-owned
dependencies with a standalone inference environment.

Rules:

- Use the committed `uv.lock` for the development environment.
- Install development dependencies through `mise run deps` and verify them with
  `mise run deps:verify`.
- Review dependency and lock changes. Do not bypass a resolver conflict or copy
  vulnerability exceptions from another project.
- Prefer compatible wheels. Review any required source build and its tools.
- Use a single trusted package index. Do not add `--extra-index-url` for private
  packages; use a controlled index or reviewed local wheels.
- For a fully locked standalone installation, pin all direct and transitive
  packages and verify local SHA-256 hashes. Do not imply that the connector's
  bounded host requirements lock the whole ComfyUI installation.
- Use `--no-deps` only after the selected environment's required packages have
  been resolved and installed.
- Install the local project through the package installer. Do not use
  `python setup.py install`, `python setup.py develop`, or `easy_install`.
- Do not change host dependencies merely to satisfy development tooling.
- Audit the resolved Python dependencies with `mise run audit:python`.

Build the actual ComfyUI distribution with `mise run release:package`. Install that
artifact into the local host for manual verification; an editable development
import is not evidence that the distributed package works.

## Module structure

Order module contents this way:

1. Module docstring.
2. `from __future__ import annotations`, when used.
3. Other module dunders, except `__all__`.
4. Imports.
5. Module constants.
6. Type aliases.
7. Dataclasses and classes.
8. Functions.
9. `if __name__ == "__main__":` guard, when the module is executable.
10. `__all__` at the bottom.

Rules:

- Every runtime module should have a module docstring that describes its present
  purpose.
- Keep top-level code limited to declarations, constants, imports, and cheap
  initialization.
- Do not perform I/O, network calls, model loading, CLI parsing, or
  long computations at import time.
- Do not mutate global runtime state at import time except for declared
  constants and deliberate local configuration.
- Keep `__all__` explicit for modules with a public API.
- Use `__all__ = []` when a module intentionally exports no public names.

Good:

```python
"""Configuration constants for runtime settings."""

from __future__ import annotations

from pathlib import Path

MODELS_DIR = Path("/models")
DEFAULT_ENGINE = "trt"


def resolve_model_dir(name: str) -> Path:
    """Return the model directory for a model name."""
    return MODELS_DIR / name


__all__ = [
    "DEFAULT_ENGINE",
    "MODELS_DIR",
    "resolve_model_dir",
]
```

Bad:

```python
from pathlib import Path

settings = read_runtime_settings()
model = AutoModel.from_pretrained("some-model")

__all__ = ["model"]
```

## Imports

Rules:

- Put imports at the top of the file, after the module docstring and future
  imports.
- Keep ordinary imports in one flat block. Do not separate standard-library,
  third-party, first-party, or sibling imports with blank lines.
- Put one-line imports before multiline or explicitly parenthesized imports.
- Sort one-line imports by the total rendered statement length. Break equal
  lengths by case-insensitive statement text and then exact statement text.
- Sort multiline or explicitly parenthesized imports by the rendered import
  header length using the same text tie-breakers.
- Sort names inside grouped imports by rendered name length using the same text
  tie-breakers.
- Apply the same ordering and spacing rules inside a top-level bare
  `if TYPE_CHECKING:` body.
- Put a blank line after each completed import block.
- Use one import per line for ordinary imports.
- Import typing and `collections.abc` symbols directly.
- Use explicit relative imports throughout the runtime package. ComfyUI loads
  the extension under its own custom-node namespace.
- Tooling may use absolute imports from its own repository packages.
- Never use implicit relative imports.
- Never use wildcard imports.
- Never import inside function, method, or class bodies in runtime code.
- Never use dynamic imports through `importlib.import_module`, `__import__`, or
  `builtins.__import__` in runtime code.
- Do not rely on the main script directory being present on `sys.path`.
- Avoid circular imports by moving shared data or contracts into a lower-level
  owner.

Good:

```python
from __future__ import annotations

import torch
import logging
from pathlib import Path
from .runtime import RuntimeConfig
from .registry import SUPPORTED_MODELS
from .configuration.settings import Settings
from collections.abc import Iterable, Sequence
```

Bad:

```python
import os, sys
from examples import *


def build():
    import src.runtime.settings
```

Direct symbol imports are acceptable for public classes, functions, constants,
and typing symbols when they make the call site clearer:

```python
from pathlib import Path
from typing import Literal
from dataclasses import dataclass
from .configuration.settings import Settings
```

Use module imports when the module prefix makes ownership clearer:

```python
import random
import logging

logger = logging.getLogger(__name__)
rng = random.Random(seed)  # noqa: S311
```

Do not import a module only to hide a vague name:

```python
from storage.file_system import options as fs_options
```

Use aliases only when:

- two imported modules have the same final name;
- an imported module conflicts with a local top-level name;
- the original module name is inconveniently long;
- the alias is a standard abbreviation, such as `np` for NumPy;
- the alias disambiguates a generic module name.

## Public and internal interfaces

Rules:

- Public names are names intended for callers outside the module.
- Internal names use one leading underscore.
- Do not use double-leading underscores unless avoiding subclass collisions in a
  class designed for inheritance.
- Do not invent double-leading and double-trailing dunder names.
- Use `__all__` for deliberate public re-exports and the root host entrypoint.
  Internal runtime modules do not need duplicate export inventories.
- Imported names are implementation details unless explicitly exported through
  `__all__` or documented as module API.
- Do not rely on indirect access to names imported by another module.
- Public attributes should not have leading underscores.
- Internal modules, functions, constants, and attributes should have one leading
  underscore.

Good:

```python
_DEFAULT_TIMEOUT_SECONDS = 30


def _normalize_format(value: str) -> str:
    return value.strip().lower()


def build_model_settings(model: str, recording_format: str) -> ModelSettings:
    """Build model settings for one runtime."""
    return ModelSettings(model=model, recording_format=_normalize_format(recording_format))


__all__ = [
    "build_model_settings",
]
```

Bad:

```python
def __normalize_label__(value):
    return int(value)
```

## Formatting

Use Ruff format as the source of truth for mechanical formatting.

Rules:

- Do not fight the formatter.
- Do not hand-align code in ways the formatter will undo.
- Do not use semicolons.
- Do not put multiple statements on one line.
- Keep formatting consistent with the surrounding file when the formatter allows
  more than one readable option.

### Indentation

Rules:

- Use 4 spaces per indentation level.
- Never use tabs.
- Use implicit continuation inside parentheses, brackets, and braces.
- Prefer hanging indents with one argument or item per line when a call or
  literal is too long.
- When using a hanging indent, put no arguments on the first line.
- Align closing delimiters with the construct start when the values are split
  across lines.

Good:

```python
result = long_function_name(
    first_argument,
    second_argument,
    third_argument,
)
```

Good:

```python
result = long_function_name(first_argument, second_argument, third_argument)
```

Bad:

```python
result = long_function_name(first_argument, second_argument, third_argument)
```

Long conditionals may use extra indentation to distinguish the condition from
the body:

```python
if config is None or "editor.language" not in config or config["editor.language"].use_spaces is False:
    use_tabs()
```

### Line length and wrapping

Rules:

- Local Python code uses the Ruff limit of 120 characters.
- Prefer shorter lines when they are naturally readable.
- Keep docstring summary lines concise and on one physical line.
- Wrap long expressions with implicit continuation inside parentheses, brackets,
  and braces.
- Do not use backslashes for line continuation.
- Break before binary operators in new multiline arithmetic or boolean
  expressions when that improves readability.
- Prefer breaking at the highest syntactic level.
- Do not split a name from its type annotation unless the name and type together
  cannot fit readably.
- Put long URLs on their own comment line instead of splitting them.

Good:

```python
income = gross_wages + taxable_interest + (dividends - qualified_dividends) - ira_deduction - student_loan_interest
```

Bad:

```python
income = gross_wages + taxable_interest + (dividends - qualified_dividends) - ira_deduction - student_loan_interest
```

Good:

```python
message = "This long string is split through implicit literal concatenation inside parentheses."
```

Bad:

```python
message = "This long string is split with an explicit continuation character."
```

### Blank lines

Rules:

- Use two blank lines between top-level function and class definitions.
- Use one blank line between methods inside a class.
- Use one blank line between a class docstring and the first method.
- Use blank lines inside functions sparingly to separate logical sections.
- Do not add blank lines immediately after a `def` line.
- Do not use large blank-line blocks as visual decoration.

Good:

```python
def build_examples() -> list[PromptExample]:
    """Build examples."""
    return []


def count_examples(examples: list[PromptExample]) -> int:
    """Return the number of examples."""
    return len(examples)
```

Bad:

```python
def build_examples() -> list[PromptExample]:

    return []
```

### Whitespace

Rules:

- Do not use extra whitespace inside parentheses, brackets, or braces.
- Do not use whitespace before commas, semicolons, or colons.
- Use one space after commas and colons, except at the end of a line.
- Do not use whitespace before the opening parenthesis of a function call.
- Do not use whitespace before indexing or slicing brackets.
- Surround assignment, augmented assignment, comparisons, identity checks,
  membership checks, and boolean operators with one space on each side.
- Use judgment around arithmetic operators, but never use more than one space on
  either side.
- Do not vertically align assignments, comments, dictionary colons, or other
  tokens with extra spaces.
- Do not leave trailing whitespace.

Good:

```python
spam(ham[1], {"eggs": 2})
x = 1
long_name = 2
if value is not None:
    return value
```

Bad:

```python
spam(ham[1], {"eggs": 2})
x = 1
long_name = 2
if value == None:
    return value
```

For slices, treat the colon like a low-priority binary operator when both sides
are complex. Omit spaces when an endpoint is omitted.

Good:

```python
items[1:9]
items[:9]
items[lower + offset : upper + offset]
items[: upper_fn(x) : step_fn(x)]
```

Bad:

```python
items[1:9]
items[lower + offset : upper + offset]
items[:upper]
```

### Trailing commas

Rules:

- Use a trailing comma in multiline literals, argument lists, imports, and
  `__all__`.
- Do not use a redundant trailing comma when the closing delimiter is on the
  same line.
- Use a trailing comma for a one-item tuple, preferably inside parentheses.

Good:

```python
FILES = ("setup.cfg",)

VARIANTS = [
    "trt",
    "vllm",
    "awq",
]
```

Bad:

```python
FILES = ("setup.cfg",)
VARIANTS = [
    "trt",
    "vllm",
]
```

### Parentheses

Rules:

- Use parentheses for grouping, tuples, and implicit line continuation.
- Do not wrap simple conditions in unnecessary parentheses.
- Do not wrap simple return values in unnecessary parentheses.
- Parenthesize one-item tuples for clarity.
- Returning a tuple may use parentheses when it improves readability.

Good:

```python
if is_ready:
    return value

singleton = (value,)
return first, second
```

Bad:

```python
if is_ready:
    return value
```

### String quotes

Rules:

- Use double quotes for ordinary strings in new code.
- Use single quotes only when it avoids escaping or matches surrounding code the
  formatter preserves.
- Use triple double quotes for docstrings.
- Prefer triple double quotes for multiline strings.
- Do not create string literals with significant trailing whitespace.
- Use `textwrap.dedent()` when a multiline string should not include indentation.

Good:

```python
name = "ModernBERT"
message = "It's ready."
doc = """One multiline string."""
```

Bad:

```python
name = "ModernBERT"
doc = """A docstring-like string."""
```

## Naming

Follow [`NAMING.md`](NAMING.md) for all naming choices.

Python-specific rules from the source guides:

- Packages and modules use short, lowercase names. Use underscores when they
  improve readability.
- Classes use CapWords.
- Exceptions use CapWords and end with `Error` when they represent errors.
- Functions, methods, parameters, local variables, and instance variables use
  lowercase words separated by underscores.
- Constants use uppercase words separated by underscores.
- Type aliases use CapWords, with one leading underscore for internal aliases.
- Private unconstrained type variables may use `_T` and `_P`.
- Avoid single-character names except for narrow counters, iterators, exception
  aliases such as `e`, file handles such as `f`, private unconstrained type
  variables, and established mathematical notation.
- Never use `l`, `O`, or `I` as single-character names.
- Use `self` for instance methods and `cls` for class methods.
- If a parameter would conflict with a keyword, append one trailing underscore.

Good:

```python
class TrainingConfig:
    """Training configuration."""


def build_examples(source_items: list[object]) -> list[PromptExample]:
    """Build examples from raw items."""
    ...


MAX_EXAMPLES = 1000
class_: str
```

Bad:

```python
class runtime_config: ...


def buildExamples(data): ...


maxExamples = 1000
clss = "value"
```

## Comments and docstrings

Comments and docstrings must match [`GENERAL.md`](GENERAL.md).

Rules:

- Describe present behavior only.
- Do not include change history.
- Do not mention removed, replaced, renamed, or previous code.
- Do not reference specific file paths unless the reference is essential and
  stable.
- Keep comments and docstrings accurate when behavior changes.
- Use clear English.
- Use complete sentences for block comments and docstrings.
- Keep punctuation, spelling, and grammar clean.

### Comments

Rules:

- Use comments to explain intent, invariants, edge cases, and non-obvious
  choices.
- Do not narrate obvious code.
- Block comments apply to the code that follows and use `#` plus one space on each line.
- Inline comments are separated from code by at least two spaces and start with
  `#` plus one space.
- Use inline comments sparingly.
- Keep comments up to date when code changes.

Good:

```python
# Longformer uses the first token for global attention in classification.
global_attention_mask[:, 0] = 1
```

Bad:

```python
global_attention_mask[:, 0] = 1  # Set item to one
```

When suppressing a linter warning, keep the suppression narrow and explain it
when the symbolic name is not enough:

```python
rng = random.Random(seed)  # noqa: S311
```

Do not add broad suppressions:

```python
# noqa
```

### Docstrings

Rules:

- Use triple double quotes for all docstrings.
- Write docstrings for public modules, functions, classes, and methods.
- Write docstrings for nontrivial private functions and methods.
- Do not write noisy docstrings for obvious private helpers.
- One-line docstrings stay on one line and end with punctuation.
- Multiline docstrings start with a one-line summary, then a blank line, then
  details.
- Put the closing triple quotes of a multiline docstring on their own line.
- Do not restate the signature in a docstring.
- Document arguments, return values, yielded values, side effects, and raised
  exceptions when they are part of the interface.
- Do not document exceptions raised only when callers violate the documented
  contract.
- Keep docstring style consistent within a file. Descriptive style and
  imperative style are both allowed by the source material.

Good one-line docstring:

```python
def build_token_budget(prompt_tokens: int, output_tokens: int) -> int:
    """Return the total token budget."""
    return prompt_tokens + output_tokens
```

Bad one-line docstring:

```python
def build_token_budget(prompt_tokens: int, output_tokens: int) -> int:
    """build_token_budget(prompt_tokens, output_tokens) -> int"""
    return prompt_tokens + output_tokens
```

Good multiline docstring:

```python
def fetch_rows(keys: Sequence[str]) -> Mapping[str, tuple[str, ...]]:
    """Fetch rows for the requested keys.

    Retrieves one row for each key that exists in the backing table.

    Args:
        keys: Keys to fetch.

    Returns:
        A mapping from key to row values.

    Raises:
        OSError: The backing table could not be read.
    """
```

### Module docstrings

Rules:

- Runtime modules should start with a docstring describing the module's purpose.
- A module docstring may include a short usage example when it helps callers.
- Test modules do not need a module docstring unless they need unusual setup,
  environment, or update instructions.

Good:

```python
"""Validated recording and connection settings for ComfyUI nodes."""
```

Bad:

```python
"""Tests for loader."""
```

### Function and method docstrings

Rules:

- Public functions and methods require docstrings.
- Nontrivial private helpers require docstrings.
- Functions with non-obvious logic require docstrings.
- Functions that mutate an argument must say so.
- Generator functions use `Yields:` instead of `Returns:`.
- `Returns:` may be omitted when the one-line summary already fully describes
  the returned value.
- Do not document `None` returns unless it clarifies control flow.
- Use `Args:`, `Returns:`, `Yields:`, and `Raises:` sections when needed.
- Keep section indentation consistent within a file.

Good:

```python
def build_engine_settings(
    recording_format: str | None,
    trt_engine_dir: str,
    default_max_batched_tokens: int,
) -> EngineSettings:
    """Build recording settings from validated inputs.

    Args:
        recording_format: Recording format name.
        trt_engine_dir: TensorRT engine directory.
        default_max_batched_tokens: vLLM token batch limit.

    Returns:
        Resolved engine settings.
    """
```

Bad:

```python
def build_engine_settings(engine, path, tokens):
    """build_engine_settings(engine, path, tokens)."""
```

### Class docstrings

Rules:

- Public classes require docstrings.
- A class docstring starts with a one-line summary describing what an instance
  represents.
- Public attributes, excluding properties, are documented in an `Attributes:`
  section.
- Exception class docstrings describe the condition represented by the
  exception, not the raising site.
- Do not write "Class that..." as the summary.

Good:

```python
@dataclass
class RuntimePrompt:
    """Single runtime prompt example.

    Attributes:
        prompt: Normalized prompt text.
        expected_status: Expected response status.
        group: Group identifier for related prompts.
    """

    prompt: str
    expected_status: str
    group: str
```

Bad:

```python
class RuntimePrompt:
    """Class that stores a runtime prompt."""
```

Good exception docstring:

```python
class MissingModelError(Exception):
    """The requested model artifact is unavailable."""
```

Bad exception docstring:

```python
class MissingModelError(Exception):
    """Raised when model loading fails."""
```

### Property docstrings

Rules:

- Property docstrings describe the attribute, not the method action.
- Use attribute-style wording.
- Do not write "Returns..." for a property unless the surrounding file already
  uses that style.

Good:

```python
@property
def num_labels(self) -> int:
    """The number of supported runtime labels."""
    return len(self.labels)
```

Bad:

```python
@property
def num_labels(self) -> int:
    """Returns the number of supported runtime labels."""
    return len(self.labels)
```

### Override docstrings

Rules:

- An overridden method may omit a docstring when it is decorated with
  `@override` and does not materially change the base contract.
- Add a docstring when an override changes behavior, side effects, constraints,
  or return semantics.
- Use `typing.override` when available in the target runtime. Use
  `typing_extensions.override` when needed.

Good:

```python
from typing_extensions import override


class Child(Parent):
    @override
    def build(self) -> Result:
        return super().build()
```

### TODO comments

Rules:

- Use TODO comments only for temporary, tracked work.
- A TODO starts with `TODO:`, then a link or issue reference, then `-`, then an
  explanation.
- Do not use individual names or team names as TODO ownership.
- Do not add TODOs for vague future improvements.
- Include a specific event or date when the TODO depends on time or an external
  milestone.

Good:

```python
# TODO: https://example.com/issues/123 - Remove this branch when all exports use JSONL.
```

Bad:

```python
# TODO: clean this up later
# TODO(alex): fix this
```

## Type annotations

Type annotations improve readability and catch type-related errors. They are
especially important for public APIs, stable code, complex data shapes, and
model or data boundaries.

### Annotation scope

Rules:

- Annotate public APIs.
- Annotate functions whose types are hard to infer.
- Annotate data structures crossing module boundaries.
- Annotate code that is prone to type-related errors.
- Annotate code when it becomes stable from a type perspective.
- Do not annotate `self` or `cls` unless needed for precise typing.
- Do not annotate `__init__` as returning `None` unless local tooling or
  surrounding style requires it.
- Use `Any` only when the type should genuinely be unconstrained or cannot be
  expressed clearly.
- Do not add obsolete `# type:` comments.
- Prefer modern Python 3.12 shorthand syntax over older `typing.Union`,
  `typing.Optional`, `typing.List`, `typing.Dict`, and `typing.Type` aliases.

Good:

```python
def build_examples(source: Literal["prompt", "image"] = "prompt") -> list[PromptExample]:
    """Build examples for a data source."""
```

Acceptable for a private helper when the body is obvious and local:

```python
def _token_count(value):
    return int(value)
```

Better when the helper is part of a typed flow:

```python
def _token_count(value: int) -> int:
    return int(value)
```

### Annotated metadata

Rules:

- Use `typing.Annotated` when a framework or validation library needs metadata
  attached to a normal Python type.
- Put the real type first. Put framework or validation metadata after it.
- Keep defaults as ordinary Python parameter defaults when using
  `Annotated`.
- Do not put conflicting defaults in both the metadata object and the function
  signature.
- Do not use arbitrary string metadata as a substitute for clear domain types,
  validators, or documented framework metadata.
- Prefer `Annotated` over older framework styles that replace the Python
  default value with a metadata object.

Good:

```python
def read_items(q: Annotated[str | None, Query(max_length=50)] = None) -> list[Item]:
    return find_items(query=q)
```

Bad:

```python
def read_items(q: str | None = Query(default=None, max_length=50)) -> list[Item]:
    return find_items(query=q)
```

Bad conflicting defaults:

```python
def read_items(q: Annotated[str, Query(default="recent")] = "popular") -> list[Item]:
    return find_items(query=q)
```

### Using Any and Object

Rules:

- Use `object` when a value can be literally any Python object and the function
  only uses operations available on all objects, such as passing the value to
  `str()`.
- Use `object` for callback return values when the callback return value is
  ignored.
- Use `Any` when the type cannot be expressed accurately, the correct type would
  make the API unreasonably hard to use, or the value intentionally escapes type
  checking.
- Do not use `Any` just to avoid writing a precise type.
- Prefer a protocol, type variable, overload, or small value object over `Any`
  when that models the contract clearly.

Good:

```python
def format_for_display(value: object) -> str:
    """Format any object for display."""
    if isinstance(value, int):
        return f"{value:02}"
    return str(value)


def call_callback(callback: Callable[[int], object]) -> None:
    """Call a callback and ignore its return value."""
    callback(42)
```

Bad:

```python
def format_for_display(value: Any) -> str:
    return str(value)


def call_callback(callback: Callable[[int], None]) -> None:
    callback(42)
```

### Input and return types

Rules:

- For arguments, prefer protocols and abstract collection types such as
  `Iterable`, `Sequence`, `Mapping`, and `Callable`.
- For arguments that accept any value, use `object`, not `Any`.
- For concrete implementations, return concrete types such as `list`, `dict`,
  and concrete dataclasses.
- For protocols and abstract base classes, choose return types case by case
  based on the promised interface.
- Avoid union return types when callers must immediately branch with
  `isinstance()` to use the result.
- If different result shapes require different caller behavior, prefer separate
  functions, a tagged dataclass, a protocol, or a small hierarchy with a clear
  common contract.
- Use `float` instead of `int | float` for numeric APIs where integers are valid
  float inputs.
- Use `None`, not `Literal[None]`.

Good:

```python
def map_lengths(values: Iterable[str]) -> list[int]:
    return [len(value) for value in values]


def create_label_map() -> dict[str, int]:
    return {"reject": 0, "accept": 1}


def to_display_text(value: object) -> str:
    return str(value)
```

Bad:

```python
def map_lengths(values: list[str]) -> list[int]:
    return [len(value) for value in values]


def create_label_map() -> MutableMapping[str, int]:
    return {"reject": 0, "accept": 1}


def to_display_text(value: Any) -> str:
    return str(value)
```

### Typing imports

Rules:

- Import symbols from `typing` and `collections.abc` directly.
- Prefer `collections.abc` abstract containers for input types.
- Prefer built-in generic types such as `list[str]`, `dict[str, int]`, and
  `tuple[str, ...]`.
- Do not use `typing.List`, `typing.Dict`, or `typing.Tuple` in new Python 3.12
  code.
- Do not use `typing.Type`; use built-in `type`.
- Do not use `typing.Union` or `typing.Optional`; use `|`.
- Do not use `typing.Text` in new code.
- Use `str` for text and `bytes` for binary data.
- Use `AnyStr` only when multiple string annotations must all be the same text
  or binary type.

Good:

```python
from collections.abc import Iterable, Mapping, Sequence
from typing import Any, Literal, TypeAlias


def transform(rows: Sequence[tuple[str, int]]) -> Mapping[str, int]: ...
```

Bad:

```python
from typing import Dict, List, Tuple, Type


def transform(rows: List[Tuple[str, int]]) -> Dict[str, int]: ...


def build(cls: Type[ModelConfig]) -> ModelConfig: ...
```

### None and optional values

Rules:

- Use explicit `X | None` for nullable values.
- Put `None` last in union annotations.
- Do not rely on implicit optional inference from a default of `None`.
- Use `is None` and `is not None` for None checks.
- When a parameter is nullable and has a default, annotate it as nullable.

Good:

```python
def read_examples(path: Path | None = None) -> list[PromptExample]:
    if path is None:
        path = DEFAULT_DATA_PATH
    ...
```

Bad:

```python
def normalize(value: None | str) -> str: ...


def read_examples(path: Path = None) -> list[PromptExample]:
    path = path or DEFAULT_DATA_PATH
```

### Generic types

Rules:

- Specify type parameters for generic types.
- Do not write bare `Sequence`, `Mapping`, `list`, or `dict` unless the element
  type is intentionally unconstrained and made explicit with `Any`.
- Prefer `TypeVar` when a relationship between input and output types matters.

Good:

```python
def get_names(employee_ids: Sequence[int]) -> Mapping[int, str]: ...
```

Bad:

```python
def get_names(employee_ids: Sequence) -> Mapping: ...
```

Good when the key type should be preserved:

```python
_T = TypeVar("_T")


def get_names(employee_ids: Sequence[_T]) -> Mapping[_T, str]: ...
```

### Type aliases

Rules:

- Use type aliases for complex repeated types.
- Type alias names use CapWords.
- Internal type aliases use one leading underscore.
- Use Python 3.12 `type` statements for new type aliases when they improve
  clarity and the surrounding module already uses Python 3.12 syntax.
- Keep `TypeAlias` for existing aliases when changing syntax would create
  unrelated churn.
- Do not use `TypeAlias` for ordinary value, module, class, function, constant,
  or path aliases.

Good:

```python
from typing import TypeAlias

_LossAndGradient: TypeAlias = tuple[torch.Tensor, torch.Tensor]
MetricMap: TypeAlias = Mapping[str, float]
Path = pathlib.Path
ERROR_EXISTS = errno.EEXIST
```

Bad:

```python
_LossAndGradient = tuple[torch.Tensor, torch.Tensor]
Path: TypeAlias = pathlib.Path
ERROR_EXISTS: TypeAlias = errno.EEXIST
```

### Type variables

Rules:

- Private unconstrained type variables may use `_T`, `_P`, and similar short
  names.
- Public or constrained type variables must have descriptive names.
- Use `_co` and `_contra` suffixes for covariant and contravariant variables.
- Do not use public single-letter `T` or `P` for type variables.

Good:

```python
from collections.abc import Callable
from typing import ParamSpec, TypeVar

_P = ParamSpec("_P")
_T = TypeVar("_T")
AddableType = TypeVar("AddableType", int, float, str)
AnyFunction = TypeVar("AnyFunction", bound=Callable)
```

Bad:

```python
T = TypeVar("T")
_F = TypeVar("_F", bound=Callable)
_T = TypeVar("_T", int, float, str)
```

### Forward references

Rules:

- Prefer `from __future__ import annotations` for forward references.
- Do not remove `from __future__ import annotations` only because newer Python
  versions defer annotation evaluation. This repository still targets Python
  3.12 and keeps future annotations as the local convention.
- Use string annotations only when future annotations are not available or when
  needed for a type-checking-only import pattern.
- Avoid type-only circular imports. They are design pressure to move shared
  contracts.

Good:

```python
from __future__ import annotations


class Node:
    def __init__(self, parent: Node | None = None) -> None:
        self.parent = parent
```

Acceptable when avoiding a runtime import strictly for typing:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from external_package import ExternalType


def build(value: "ExternalType") -> str: ...
```

### Protocols and interfaces

Rules:

- Prefer `typing.Protocol` for structural interfaces used by a consumer.
- Keep protocols narrow. Define only the attributes and methods the consumer
  needs.
- Place a protocol near the consumer when it describes what that consumer needs,
  not what an implementation happens to provide.
- Use `@runtime_checkable` only when runtime `isinstance()` checks are truly
  needed.
- Use abstract base classes when nominal identity, runtime instantiation checks,
  or a standard-library ABC contract is the real requirement.
- Do not use an abstract base class to share implementation code.
- Do not mix interface definition with subclass-based code sharing.
- Implementations do not need to import or subclass a protocol for type checkers
  to recognize that they satisfy it.

Good:

```python
class Reader(Protocol):
    def read(self) -> str: ...


def print_reader(reader: Reader) -> None:
    print(reader.read())
```

Good implementation:

```python
class FileReader:
    def read(self) -> str:
        return "contents"
```

Bad:

```python
class BaseReader(abc.ABC):
    def read_and_print(self) -> None:
        print(self.read())

    @abc.abstractmethod
    def read(self) -> str: ...
```

### Variable annotations

Rules:

- Use variable annotations when the inferred type is unclear or impossible.
- Use one space after the colon.
- Do not use a space before the colon.
- If assigning a value, use one space around `=`.

Good:

```python
examples: list[PromptExample] = []
label_by_name: dict[str, int] = {}
```

Bad:

```python
examples: list[PromptExample] = []
label_by_name: dict[str, int] = {}
```

### Ignoring type errors

Rules:

- Avoid `# type: ignore`.
- If an ignore is necessary, keep it line-scoped.
- Include the specific error code when the type checker supports it.
- Do not keep unused ignores.
- Prefer refactoring or a clearer annotation over suppressing a type error.

Good:

```python
value = untyped_api()  # type: ignore[no-any-return]
```

Bad:

```python
# type: ignore
```

## Constants, globals, and mutable state

Rules:

- Module constants are allowed and encouraged.
- Constants use uppercase names with underscores.
- Internal constants use one leading underscore.
- Avoid mutable global state.
- Do not use lazy singleton state.
- Do not create module-level `STATE`, `_STATE`, `INSTANCE`, `_INSTANCE`, or
  `_instance` holders.
- Do not expose mutable globals directly as public API.
- If mutable global state is genuinely required, keep it internal and document
  the design reason.
- Do not mutate module globals as a hidden side effect of ordinary function
  calls.

Good:

```python
DEFAULT_MODEL_NAME = "answerdotai/ModernBERT-base"
_MAX_RETRIES = 3
```

Bad:

```python
STATE = {"instance": None}
_INSTANCE = None
```

Prefer passing state explicitly:

```python
def build_client(config: ClientConfig) -> Client:
    return Client(config)
```

Do not hide process-wide state behind lifecycle helpers:

```python
def get_instance() -> Client: ...
```

## Functions and methods

Rules:

- Keep functions focused on one responsibility.
- Prefer plain functions and explicit data flow before classes.
- Name functions by action and domain concept.
- Do not use `process`, `handle`, `run`, `execute`, or `do_work` when a more
  precise action exists.
- Use `handle` only for callbacks, framework boundaries, event handlers, or
  signal handlers.
- Keep side effects explicit in the name or docstring.
- Do not hide I/O in helpers that look like pure transformations.

### Function size

Rules:

- Keep functions small and focused.
- Custom lint limits functions and methods to 60 counted code lines by default.
- If a function approaches the limit, consider extracting real sub-operations.
- Do not split a function into meaningless helpers only to satisfy the count.
- Extract helpers when the extracted operation has a clear name and contract.

Good extraction:

```python
def _trim_history_messages(
    messages: Sequence[HistoryMessage],
    max_messages: int,
) -> list[HistoryMessage]:
    if len(messages) <= max_messages:
        return list(messages)
    return list(messages[-max_messages:])
```

Bad extraction:

```python
def _part_one(data): ...


def _part_two(data): ...
```

### Default arguments

Rules:

- Do not use mutable objects as default argument values.
- Use `None` as the default and create the mutable value inside the function.
- Immutable defaults such as `None`, strings, numbers, booleans, and tuples are
  allowed.
- Do not use dynamic values such as `time.time()` as defaults.
- Do not use parsed flag values, environment-dependent values, or mutable global
  values as defaults.
- When an annotated parameter has a default, put spaces around `=`.
- When an unannotated parameter has a default, do not put spaces around `=`.

Good:

```python
def collect_labels(labels: Sequence[str] | None = None) -> list[str]:
    if labels is None:
        labels = []
    return list(labels)
```

Bad:

```python
def collect_labels(labels: list[str] = []) -> list[str]:
    return labels
```

Good formatting:

```python
def resize(width: int = 0, height: int = 0) -> None: ...
```

Bad formatting:

```python
def resize(width: int = 0, height: int = 0) -> None: ...
```

### Return statements

Rules:

- Be consistent in return statements.
- If any return statement returns a value, every no-value path should explicitly
  return `None` or end in a clear final return.
- Do not mix `return` and `return value` in the same function.
- Do not rely on implicit `None` when an explicit no-result path is meaningful.

Good:

```python
def safe_sqrt(value: float) -> float | None:
    if value < 0:
        return None
    return math.sqrt(value)
```

Bad:

```python
def safe_sqrt(value: float) -> float | None:
    if value >= 0:
        return math.sqrt(value)
```

### Nested functions and classes

Rules:

- Nested functions are allowed when they close over a local value and make the
  outer function clearer.
- Nested classes are allowed for narrowly scoped helper types.
- Do not nest a function only to hide it from users.
- Prefer a module-level private helper when real callers need direct access.
- Avoid nested functions that make the outer function long or hard to scan.

Good:

```python
def get_adder(summand: float) -> Callable[[float], float]:
    """Return a function that adds a fixed summand."""

    def add(value: float) -> float:
        return summand + value

    return add
```

Bad:

```python
def build_examples(data: list[object]) -> list[PromptExample]:
    def normalize_prompt(value: object) -> str:
        return str(value).strip()

    ...
```

Use a module helper instead:

```python
def _normalize_prompt(value: object) -> str:
    return str(value).strip()
```

### Lambda functions

Rules:

- Lambdas are allowed for simple one-line expressions.
- Do not bind a lambda directly to a name. Use `def`.
- Prefer generator expressions over `map()` or `filter()` with a lambda.
- Use functions from `operator` for common operations when they are clearer.
- If a lambda spans multiple lines or becomes hard to read, use a named
  function.

Good:

```python
def double(value: int) -> int:
    return value * 2


sorted_items = sorted(items, key=lambda item: item.name)
```

Bad:

```python
double = lambda value: value * 2
```

### Conditional expressions

Rules:

- Conditional expressions are allowed for simple cases.
- Each portion should be easy to read: true expression, condition, false
  expression.
- Use a full `if` statement when the expression becomes long or nested.

Good:

```python
mode = "stream" if is_streaming else "batch"
```

Bad:

```python
mode = (
    choose_streaming_mode(request, config)
    if complicated_condition(request, config, metadata)
    else choose_batch_mode(request, config, metadata)
)
```

### Comprehensions and generator expressions

Rules:

- Use comprehensions for simple mapping or filtering.
- Do not use multiple `for` clauses or multiple filter expressions in one
  comprehension.
- Optimize for readability, not compactness.
- Use ordinary loops for nested logic, multiple conditions, mutation, or
  non-obvious transformations.
- Generator expressions are preferred when a list is not needed.

Good:

```python
names = [user.name for user in users if user is not None]
```

Good with a long expression:

```python
valid_examples = [transform_example(example) for example in examples if is_valid_example(example)]
```

Bad:

```python
pairs = [(x, y) for x in range(10) for y in range(5) if x * y > 10]
```

Use a loop:

```python
pairs: list[tuple[int, int]] = []
for x in range(10):
    for y in range(5):
        if x * y > 10:
            pairs.append((x, y))
```

### Generators

Rules:

- Use generators when values can be produced lazily.
- A generator docstring uses `Yields:`.
- If a generator manages an expensive resource, make cleanup explicit.
- Do not keep resource lifetime implicit in a partially consumed generator.

Good:

```python
def iter_prompt_text(examples: Iterable[PromptExample]) -> Iterable[str]:
    """Yield prompt text values.

    Yields:
        Prompt text values.
    """
    for example in examples:
        yield example.prompt
```

## Classes

### Class design

Rules:

- Prefer functions and data structures unless a class owns real state,
  invariants, or behavior.
- Keep one top-level non-dataclass class per file.
- Related dataclasses may live together when they form one small data contract.
- Do not create classes only to group static functions.
- Avoid `Manager`, `Processor`, `Helper`, and similar vague class names.
- Decide deliberately which attributes are public and which are internal.
- Use public attributes for simple data.
- Use one leading underscore for internal attributes.
- Avoid double-leading underscores unless protecting a base class from subclass
  name collisions.
- Focus on the shape of data before adding behavior.
- If a function coordinates work between multiple classes and no polymorphism is
  involved, keep it a function unless one class clearly owns the behavior.

Good:

```python
class RuntimeBatch:
    """Validated prompts prepared for generation."""
```

Bad:

```python
class RuntimeManager:
    """Class that manages runtime work."""
```

### Initialization and named constructors

Rules:

- Keep `__init__` small.
- `__init__` should accept the values the class needs, not complex external
  objects that happen to contain those values.
- Do not couple a class constructor to database rows, ORM objects, API payloads,
  CLI namespaces, or provider SDK response objects.
- Use classmethod named constructors for external representations, such as
  `from_row`, `from_payload`, `from_token`, or `from_path`.
- Do not construct business objects with `ClassName(**external_attributes)` when
  that couples the class to an external storage or wire format.
- Validation of class invariants belongs in initialization.
- Complex loading, serialization, deserialization, and validation systems should
  stay outside the business object.
- Derived attributes should be cheap, deterministic, and based on already
  initialized fields. Prefer a named constructor when deriving them requires I/O,
  external services, or complex parsing.

Good:

```python
@dataclass
class Point:
    """Two-dimensional point."""

    x: float
    y: float

    @classmethod
    def from_row(cls, row: PointRow) -> Point:
        """Build a point from a database row."""
        return cls(x=row.x, y=row.y)
```

Bad:

```python
class Point:
    def __init__(self, database_row):
        self.x = database_row.x
        self.y = database_row.y


point = Point(**row.attributes)
```

### Dataclasses

Rules:

- Use dataclasses for plain data records.
- Keep dataclass fields typed.
- Document public fields in the class docstring `Attributes:` section when the
  class is public.
- Do not add methods to a dataclass unless they are part of the data contract.
- Do not use a dataclass as a disguised mutable global configuration object.
- Use `field(default_factory=...)` for mutable defaults.
- Use `__post_init__` for simple invariant checks or cheap derived fields.
- Prefer a named constructor over `__post_init__` when construction needs
  parsing, I/O, external objects, or multiple alternate sources.
- If a project already uses `attrs`, apply the same principles: use factories
  for mutable defaults, validators for invariants, converters for simple input
  normalization, and named constructors for complex creation paths.
- Do not introduce `attrs` solely to avoid writing a small dataclass or ordinary
  function.

Good:

```python
@dataclass(frozen=True)
class ModelVariant:
    """Supported model variant.

    Attributes:
        name: Stable variant name.
        base_model: Provider model identifier.
    """

    name: str
    base_model: str
```

Good mutable default:

```python
@dataclass
class Batch:
    """Batch of prompts."""

    prompts: list[PromptExample] = field(default_factory=list)
```

Bad mutable default:

```python
@dataclass
class Batch:
    prompts: list[PromptExample] = []
```

### Properties

Rules:

- Use properties only for cheap, straightforward, unsurprising attribute access.
- Do not use a property to simply get and set an internal attribute.
- Do not hide expensive work behind attribute syntax.
- Do not hide side effects behind properties.
- Use `@property`; do not manually implement descriptors unless the power
  feature is necessary.
- Avoid properties for computations subclasses may need to override and extend.

Good:

```python
@property
def num_examples(self) -> int:
    """The number of examples."""
    return len(self.examples)
```

Bad:

```python
@property
def model(self) -> AutoModel:
    return AutoModel.from_pretrained(self.model_name)
```

### Inheritance

Rules:

- Design explicitly for inheritance or avoid inheritance.
- Prefer composition over inheritance for code sharing.
- Do not subclass only to reuse methods or state.
- Do not use the template method pattern as a default design. A base class that
  defines control flow and calls subclass hooks is harder to read and easier to
  break than a wrapper with explicit delegation.
- Do not mix three different inheritance purposes in one hierarchy: code
  sharing, interface definition, and specialization.
- Use protocols or small ABCs for interfaces.
- Use specialization only when the subclass truly is the base class plus more
  and can be used anywhere the base class is expected.
- Follow the Liskov substitution principle: callers that accept the base class
  must be able to interact correctly with the subclass.
- Keep strict specialization hierarchies shallow and physically close together
  when practical.
- Do not model variants as one class with a type field and many optional fields
  that only apply for some type values.
- Make invalid states unrepresentable where practical.
- Use composition when behavior varies across more than one axis.
- Use a wrapper when you need one behavior plus cross-cutting behavior such as
  tracking, caching, timing, or logging.
- Consider `functools.singledispatch` when an operation varies by type but does
  not clearly belong to one class.
- Public attributes have no leading underscore.
- Internal attributes use one leading underscore.
- Double-leading underscores are only for avoiding accidental subclass name
  collisions.
- If a class is intended for subclassing, document the public API and subclass
  API separately when that distinction matters.

Good specialization:

```python
@dataclass
class EmailAddress:
    """Email address shared by all address types."""

    id: UUID
    address: str


@dataclass
class Mailbox(EmailAddress):
    """Email address that stores mail."""

    password_hash: str
```

Bad optional-field variant:

```python
@dataclass
class EmailAddress:
    kind: str
    id: UUID
    address: str
    password_hash: str | None
    forwarding_targets: list[str] | None
```

Good wrapper:

```python
class TrackingRepository:
    """Repository wrapper that records retrieved products."""

    def __init__(self, repository: Repository) -> None:
        self._repository = repository
        self.seen: set[Product] = set()

    def add_product(self, product: Product) -> None:
        self._repository.add_product(product)
        self.seen.add(product)
```

Bad subclass-based code sharing:

```python
class BaseRepository(abc.ABC):
    def add_product(self, product: Product) -> None:
        self._add_product(product)
        self.seen.add(product)

    @abc.abstractmethod
    def _add_product(self, product: Product) -> None: ...
```

### Decorators

Rules:

- Use decorators when they remove real repetition or express a clear framework
  contract.
- Decorator behavior must be unsurprising.
- Decorators run at definition time, usually import time. Do not let them depend
  on files, sockets, databases, network calls, or other unavailable resources.
- Decorators should preserve function metadata when wrapping functions.
- Avoid `staticmethod`. Use a module-level function instead.
- Use `classmethod` for named constructors or class-specific routines.
- Use `@property` only under the property rules above.

Good:

```python
class ModelConfig:
    @classmethod
    def from_name(cls, name: str) -> ModelConfig:
        """Build a model config from a variant name."""
        return cls(name=name)
```

Bad:

```python
class ModelConfig:
    @staticmethod
    def normalize_name(name: str) -> str:
        return name.strip().lower()
```

Use a module function:

```python
def normalize_model_name(name: str) -> str:
    return name.strip().lower()
```

### Exceptions as classes

Rules:

- Custom exceptions inherit from `Exception`.
- Do not inherit directly from `BaseException`.
- Exception class names use CapWords.
- Error exception names end with `Error`.
- Exception names should not repeat the module name.
- Exception docstrings describe the represented condition.

Good:

```python
class InvalidVariantError(Exception):
    """The requested model variant is not supported."""
```

Bad:

```python
class VariantsInvalidVariantError(BaseException):
    """Raised in variants.py when the variant is invalid."""
```

## Exceptions and error handling

Rules:

- Use built-in exception classes when they fit the error.
- Raise `ValueError` for invalid argument values.
- Raise `TypeError` for invalid argument types when type validation is needed.
- Keep `try` blocks as small as possible.
- Catch specific exceptions.
- Do not use bare `except:`.
- Do not catch `Exception` unless re-raising or creating a deliberate isolation
  boundary that records and suppresses failures.
- Use `else` when code should run only if the `try` block succeeds.
- Use `finally` for cleanup that must run regardless of success or failure.
- Do not use `return`, `break`, or `continue` in a `finally` block when an
  exception could be active.
- Use `raise NewError(...) from error` when replacing an exception but preserving
  the cause.
- Use `raise NewError(...) from None` only when deliberately suppressing an
  irrelevant implementation exception, and preserve relevant details in the new
  message.
- When catching operating-system errors, prefer Python's explicit OSError
  subclass hierarchy over checking `errno` manually.

Good:

```python
try:
    value = collection[key]
except KeyError:
    return key_not_found(key)
else:
    return handle_value(value)
```

Bad:

```python
try:
    return handle_value(collection[key])
except KeyError:
    return key_not_found(key)
```

Good exception replacement:

```python
try:
    raw_value = payload["label"]
except KeyError as error:
    raise ValueError("Missing required field: label") from error
```

Bad catch-all:

```python
try:
    start_server()
except Exception:
    return None
```

## Assertions

Rules:

- Do not use `assert` for application logic, input validation, permission
  checks, or required preconditions.
- Do not rely on `assert` to satisfy type checking or runtime correctness.
- `assert` is acceptable for non-critical internal consistency checks where
  removing it would not change application behavior.
- Use explicit `if` checks and raise exceptions for real validation.

Good:

```python
def connect_to_port(minimum: int) -> int:
    """Connect to the next available port."""
    if minimum < 1024:
        raise ValueError(f"Minimum port must be at least 1024: {minimum=}")
    port = find_next_open_port(minimum)
    if port is None:
        raise ConnectionError(f"Could not connect on or above port: {minimum=}")
    assert port >= minimum
    return port
```

Bad:

```python
def connect_to_port(minimum: int) -> int:
    assert minimum >= 1024
    port = find_next_open_port(minimum)
    assert port is not None
    return port
```

## Boolean logic and comparisons

Rules:

- Compare to `None` with `is None` or `is not None`.
- Do not compare booleans to `True` or `False`.
- Use truthiness for sequences and containers.
- When handling integers, compare to `0` when zero has domain meaning.
- Do not write `if not value` when `None`, `0`, `False`, and empty containers
  have different meanings.
- Use `is not` instead of `not ... is`.
- Use `isinstance()` for type checks.
- Use `startswith()` and `endswith()` for prefix and suffix checks.
- Do not compare types directly unless exact type identity is the real contract.
- For rich ordering, implement all relevant comparison operations or use
  `functools.total_ordering()`.

Good:

```python
if value is not None:
    ...

if not examples:
    ...

if count == 0:
    ...

if isinstance(obj, int):
    ...

if filename.endswith(".json"):
    ...
```

Bad:

```python
if value != None:
    ...

if greeting == True:
    ...

if len(examples) == 0:
    ...

if type(obj) is int:
    ...

if filename[-5:] == ".json":
    ...
```

NumPy arrays may reject implicit boolean evaluation. Use `.size` or another
explicit property when checking array emptiness.

## Control flow simplification

Rules:

- Reduce nesting when a condition can be merged without changing behavior.
- Merge adjacent `if` statements when the inner condition has no intervening
  work and no `else` branch that changes the result.
- Prefer guard clauses when they remove a level of nesting and keep the main
  path easy to scan.
- Hoist repeated code out of conditional branches when it runs in every branch.
- Hoist loop-invariant statements out of `for` and `while` loops when they do
  not depend on the loop variable and have no required repeated side effect.
- Do not combine conditions when separate conditions communicate distinct
  domain decisions more clearly.
- Do not hoist code when execution order, exceptions, logging, timing, database
  calls, or mutation would change.

Good merged condition:

```python
if is_enabled and has_examples:
    return build_examples()
```

Bad nested condition:

```python
if is_enabled:
    if has_examples:
        return build_examples()
```

Good hoisted branch code:

```python
if sold > DISCOUNT_AMOUNT:
    total = sold * DISCOUNT_PRICE
else:
    total = sold * PRICE
label = f"Total: {total}"
```

Bad repeated branch code:

```python
if sold > DISCOUNT_AMOUNT:
    total = sold * DISCOUNT_PRICE
    label = f"Total: {total}"
else:
    total = sold * PRICE
    label = f"Total: {total}"
```

Good loop-invariant hoist:

```python
city = "London"
for building in buildings:
    addresses.append((building.street_address, city))
```

Bad loop-invariant assignment:

```python
for building in buildings:
    city = "London"
    addresses.append((building.street_address, city))
```

Do not merge conditions when it hides separate decisions:

```python
if not request.user:
    raise PermissionError("Authentication is required")
if not request.user.can_export:
    raise PermissionError("Export permission is required")
```

## Iteration and collections

Rules:

- Use default iterators and membership operators for containers that support
  them.
- Iterate dictionaries directly for keys.
- Use `.items()` when both keys and values are needed.
- Do not call `.keys()` only to iterate keys.
- Do not call `.readlines()` only to iterate file lines.
- Do not mutate a container while iterating over it.
- Prefer clear loops over dense collection transformations.
- Use `yield from iterable` instead of a loop that only yields every item from
  another iterable.
- Use `any()` and `all()` for simple existence or universal predicate checks.
- Use `[]` for an empty list and `{}` for an empty dictionary.
- Use `list()` or `dict()` when converting an iterable or mapping, not for empty
  literals.

Good:

```python
for key in values:
    ...

for key, value in values.items():
    ...

for line in file_obj:
    ...

if item in values:
    ...
```

Bad:

```python
for key in values.keys():
    ...

for line in file_obj.readlines():
    ...
```

Good delegated yield:

```python
def get_content(entry: Entry) -> Iterable[Block]:
    yield from entry.get_blocks()
```

Bad delegated yield:

```python
def get_content(entry: Entry) -> Iterable[Block]:
    for block in entry.get_blocks():
        yield block
```

Good predicate check:

```python
found = any(thing == expected for thing in things)
all_valid = all(is_valid(thing) for thing in things)
```

Bad predicate loop:

```python
found = False
for thing in things:
    if thing == expected:
        found = True
        break
```

Good empty containers:

```python
items = []
metadata = {}
```

Bad empty containers:

```python
items = list()
metadata = dict()
```

## Strings, logging, and error messages

### String formatting

Rules:

- Use f-strings, `%` formatting, or `.format()` for formatting.
- Prefer f-strings for ordinary string interpolation.
- Do not use `+` to format strings with values.
- A single `a + b` concatenation is allowed when both values are already strings
  and this is not formatting.
- Do not accumulate strings with `+` or `+=` in a loop.
- Accumulate parts in a list and `"".join(parts)`, or use `io.StringIO`.
- Use implicit literal concatenation inside parentheses for long string
  literals.

Good:

```python
message = f"name: {name}; score: {score}"

rows = ["<table>"]
for last_name, first_name in employees:
    rows.append("<tr><td>%s, %s</td></tr>" % (last_name, first_name))
rows.append("</table>")
employee_table = "".join(rows)
```

Bad:

```python
message = "name: " + name + "; score: " + str(score)

employee_table = "<table>"
for last_name, first_name in employees:
    employee_table += "<tr><td>%s, %s</td></tr>" % (last_name, first_name)
employee_table += "</table>"
```

### Logging

Rules:

- Create loggers with `logging.getLogger(__name__)`.
- Use module-level loggers. Logger names should track the package and module
  hierarchy through `__name__`.
- Do not log through the root logger from application or library modules.
- Use `print()` for ordinary CLI output intended for the user.
- Use `logger.debug()` for detailed diagnostic information.
- Use `logger.info()` for normal operational events and status.
- Use `logger.warning()` when something unexpected happened but the software can
  still continue as expected.
- Use `warnings.warn()` in library code when client code should change to avoid
  the issue.
- Raise an exception to report an error that prevents the requested operation.
- Use `logger.error()`, `logger.exception()`, or `logger.critical()` when an
  error is deliberately suppressed at an isolation boundary and must be recorded.
- Use `logger.exception()` only inside an exception handler.
- Logging calls that accept pattern strings must use a string literal first
  argument and pass values as later arguments.
- Do not use f-strings in logging pattern calls.
- Do not call logging once for the static text and once for the value.
- Do not eagerly compute expensive logging arguments unless the log level is
  enabled. Use `logger.isEnabledFor(...)` around expensive diagnostic work.
- Configure handlers, formatters, and levels at the application entrypoint or
  deployment boundary, not in importable library modules.
- Call `logging.basicConfig()` before logger methods are called when an
  entrypoint uses basic configuration.
- If dictionary or file logging configuration is used, set
  `disable_existing_loggers` deliberately.
- Library modules must not add handlers other than `logging.NullHandler()` to
  their own top-level logger.
- Do not define custom logging levels unless there is a documented application
  need.
- Do not log secrets, tokens, passwords, PII, or full authenticated request
  bodies.
- Keep log messages precise and searchable.

Good:

```python
logger.info("Warmup prompts: %d", num_prompts)
logger.warning("Requested max_length=%d exceeds model limit; clamping to %d", requested, effective)
```

Good expensive debug logging:

```python
if logger.isEnabledFor(logging.DEBUG):
    logger.debug(
        "Tokenization details: %s",
        build_expensive_tokenization_summary(batch),
    )
```

Good exception logging:

```python
try:
    upload_model(model_dir)
except UploadError:
    logger.exception("Model upload failed")
    raise
```

Bad:

```python
logging.info("Warmup prompts: %d", num_prompts)
logger.info(f"Warmup prompts: {num_prompts}")
logger.info("Warmup prompts:")
logger.info(num_prompts)
```

Bad exception logging:

```python
logger.exception("Model upload failed")
```

### Error messages

Rules:

- Error messages must match the actual error condition.
- Interpolated values must be clearly identifiable.
- Prefer `name=value` formatting for values that aid debugging.
- Keep messages easy to grep.
- Start user-visible messages with an uppercase letter.
- Do not leak schema names, table names, file paths, internal IDs, stack traces,
  trigger names, policy names, secrets, or implementation details.
- Use generic messages for configuration and infrastructure failures unless the
  details are part of the public contract.

Good:

```python
if not 0 <= probability <= 1:
    raise ValueError(f"Not a probability: {probability=}")
```

Bad:

```python
if probability < 0 or probability > 1:
    raise ValueError(f"The probability was bad: {probability}")
```

Good logging around OS errors:

```python
try:
    workdir.rmdir()
except OSError as error:
    logger.warning("Could not remove directory (reason: %r): %r", error, workdir)
```

Bad logging:

```python
try:
    workdir.rmdir()
except OSError:
    logger.warning("Directory already was deleted: %s", workdir)
```

## Files and stateful resources

Rules:

- Explicitly close files, sockets, database connections, mmap mappings, h5py
  files, matplotlib figures, and similar stateful resources.
- Prefer `with` statements for resources that support context management.
- Use `contextlib.closing()` for closeable resources without context-manager
  support.
- Do not rely on finalizers or garbage collection for resource cleanup.
- Keep resource scope as small as practical.
- Do not return open resources from helpers unless resource ownership is part of
  the documented contract.
- Document resource lifetime when context-based management is infeasible.

Good:

```python
with path.open(encoding="utf-8") as file_obj:
    for line in file_obj:
        handle_line(line)
```

Bad:

```python
file_obj = path.open()
for line in file_obj:
    handle_line(line)
```

Good for closeable objects without context-manager support:

```python
import contextlib

with contextlib.closing(open_remote_resource(url)) as resource:
    consume(resource)
```

## Main programs and top-level code

Rules:

- Executable modules put main behavior in a `main()` function.
- Use `if __name__ == "__main__":` before executing program behavior.
- Prefer `raise SystemExit(main())` when `main()` returns an exit code.
- Do not parse CLI arguments at import time.
- Do not run model loading, network calls, or file
  mutations at import time.
- Use `python -m package.module` for repository Python entrypoints.
- Shell scripts must call Python modules, not inline Python snippets.
- Files that are not intended to execute directly do not need a shebang.
- Directly executable Python files may use `#!/usr/bin/env python3` when a
  shebang is needed.

Good:

```python
def main() -> int:
    """Run the command."""
    ...
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Bad:

```python
args = parser.parse_args()
start_server(args)
```

## Packages and architecture

Rules:

- Keep packages shallow and purposeful.
- Flatten packages that contain only `__init__.py` and one other module.
- Do not create single-file packages.
- Do not create import cycles.
- Do not create lazy module export hooks such as module-level `__getattr__`,
  `__dir__`, or `__getattribute__`.
- Do not use dynamic imports for lazy loading.
- Do not use package `__init__.py` files to hide expensive imports.
- Keep `__init__.py` files small and import-stable.
- Barrel `__init__.py` files may contain imports and `__all__`.
- Respect import-linter contracts configured in `pyproject.toml`.
- Keep lower-level packages independent of higher-level workflow packages.

### src layout and import path

Rules:

- Keep importable connector runtime code under `src/`.
- Keep the root ComfyUI entrypoint and the existing `scripts` and `quality` tooling
  packages outside it. Runtime code must not import these development packages.
- Treat the repository root as project configuration and tooling space, not as
  the import package root.
- Run Python entrypoints through the configured environment, editable install,
  project scripts, or `python -m` with the intended import path.
- Do not mutate `sys.path` in package code to make imports work.
- Do not rely on the current working directory being first on Python's import
  path.
- Do not make root-level modules importable only in development. Code that works
  only because the process starts from the repository root is not packaged
  correctly.
- Keep helper scripts that are not meant to be imported outside the package
  import path.

Good layout:

```text
.
  pyproject.toml
  README.md
  src/
    config/
      __init__.py
      runtime/
        __init__.py
        engine.py
    runtime/
      __init__.py
      settings.py
```

Bad layout:

```text
.
  pyproject.toml
  config/
    __init__.py
  runtime/
    __init__.py
```

Bad import-path patch:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
```

Current import-linter contracts keep runtime code independent of development
tools, discovery independent of execution and media, and configuration independent
of nodes and execution. The exact contracts live in `pyproject.toml`.

Good package shape:

```text
src/
  config/
    __init__.py
    runtime/
      __init__.py
      engine.py
  runtime/
    __init__.py
    settings.py
    server_start.py
```

Bad single-file package:

```text
src/
  metrics/
    __init__.py
    accuracy.py
```

Use a module instead:

```text
src/
  metrics.py
```

## Power features

Avoid power features unless the project already has a clear local pattern and
the feature is necessary.

Avoid:

- custom metaclasses;
- bytecode manipulation;
- dynamic inheritance;
- object reparenting;
- import hooks and import hacks;
- runtime monkeypatching;
- reflection-heavy designs;
- modifying interpreter internals;
- `__del__` cleanup logic;
- manual descriptor implementations;
- dynamic code generation.

Allowed standard-library uses include `dataclasses`, `enum`, and `abc` when they
fit the problem.

Rules:

- Do not use a power feature to make code shorter.
- Do not use a power feature to hide a dependency cycle or ownership problem.
- Prefer ordinary functions, dataclasses, explicit imports, and explicit data
  structures.

## Threading and concurrency

Rules:

- Do not rely on atomicity of built-in types.
- Do not rely on atomic variable assignment for synchronization.
- Use `queue.Queue` for thread communication when appropriate.
- Use `threading` locks, conditions, or higher-level primitives for shared
  state.
- Prefer `threading.Condition` over low-level polling loops.
- Keep shared mutable state small and explicit.
- Document concurrency, cancellation, and isolation behavior when present.

## Manual verification

Do not create or run automated tests. Use the configured static checks and builds.
Operate the actual installed package in Comfy Desktop when runtime verification
is required. Verify every affected node, workflow, and model with its real inputs,
outputs, live controls, cancellation, and cleanup. Keep run evidence private.

## Verification commands

Use the requested project tasks:

```bash
mise run lint:python
mise run type:python
mise run check
mise run security
```

`mise run check` covers formatting, linting, strict types, dependency consistency,
and generated-file freshness. Formatting and generation remain explicit mutation
tasks. Do not create or run automated tests, including through hooks.

Resolve host types through `COMFYUI_PATH` in ignored local configuration. Use the
actual installed ComfyUI source and its Python environment, dependency annotations,
`TYPE_CHECKING`, and narrow consumer-owned `Protocol` definitions. Do not create
`typings/`, fake host modules, or global missing-import suppressions.

Report the failing command and affected area. Fix findings in the authorized
scope; do not relax rules simply to obtain a passing result.

## Review checklist

Before finishing Python changes, review the diff for these points:

- Does the code follow local project rules over generic style preferences?
- Are imports top-level, grouped, sorted, and free of cycles?
- Is the module import-stable, with no import-time work?
- Are public APIs typed and documented?
- Do argument types accept the broadest useful protocol or abstract collection?
- Do concrete implementations return concrete types?
- Is `Any` avoided where `object`, a protocol, or a type variable would express
  the contract?
- Are names consistent with [`NAMING.md`](NAMING.md)?
- Are functions small, focused, and under the local length limit?
- Are defaults immutable or initialized inside the function?
- Are None checks explicit?
- Are constructors free of external row, payload, SDK, or CLI object coupling?
- Is subclassing used only for interfaces or true specialization, not code
  sharing?
- Are exceptions specific, with narrow `try` blocks?
- Are resources managed with `with` or documented ownership?
- Are logging calls using literal pattern strings and argument parameters?
- Is logging configured only at the application boundary?
- Are error messages precise, actionable, and free of internal details?
- Are environment variables read, parsed, and validated at a boundary instead
  of inside business logic?
- Are comments present where behavior is non-obvious and absent where they only
  narrate code?
- Is `__all__` explicit and at the bottom when public exports exist?
- Are package boundaries and import-linter contracts respected?
- Is importable code under `src/` without `sys.path` mutation?
- Did you run the requested static checks and keep automated tests excluded?

## Anti-patterns

Do not write:

```python
from module import *
```

```python
from typing import Dict, List, Optional, Type, Union
```

```python
type Rows = list[dict[str, object]]
```

```python
def format_value(value: Any) -> str:
    return str(value)
```

```python
def load(path: None | Path) -> list[str]: ...
```

```python
_Rows = list[dict[str, object]]
```

```python
Path: TypeAlias = pathlib.Path
```

```python
def f(value=[]): ...
```

```python
if value == None:
    ...
```

```python
if flag == True:
    ...
```

```python
try:
    ...
except:
    ...
```

```python
try:
    return transform(collection[key])
except KeyError:
    return fallback()
```

```python
logger.info(f"Loaded {count} prompts")
```

```python
logging.info("Loaded %d prompts", count)
```

```python
logger.exception("Upload failed")
```

```python
STATE = {"instance": None}
```

```python
def get_instance(): ...
```

```python
def build():
    import examples
```

```python
def build_client() -> Client:
    token = os.getenv("API_TOKEN", "example-token")
    return Client(token=token)
```

```python
import importlib

module = importlib.import_module("examples")
```

```python
import sys

sys.path.insert(0, "src")
```

```bash
python -m pip install -r loose-requirements.lock
python -m pip install --extra-index-url https://packages.example.com/simple private-package
python setup.py install
python setup.py develop
easy_install example-package
```

```python
def __getattr__(name: str) -> object: ...
```

```python
class TrainingManager: ...
```

```python
class Point:
    def __init__(self, row):
        self.x = row.x
        self.y = row.y
```

```python
class BaseRepository(abc.ABC):
    def add_product(self, product: Product) -> None:
        self._add_product(product)
        self.seen.add(product)
```

```python
double = lambda value: value * 2
```

```python
employee_table = ""
for row in rows:
    employee_table += render_row(row)
```

```python
if len(examples):
    ...
```

```python
if type(value) is str:
    ...
```

```python
if name[:4] == "test":
    ...
```

```python
def main(): ...


main()
```

## ComfyUI and Reactor boundaries

- Keep registration small and free of network activity. Use documented ComfyUI
  node APIs and native image, audio, and video types.
- Preserve node IDs, serialized widget and socket names, model identifiers, and
  stored settings. Change visible labels without changing saved contracts.
- Keep host imports at their boundary. Isolated media workers run by file path
  with the selected host interpreter; do not add imports that require the
  repository working directory or mutate `sys.path`.
- Validate decoded JSON at entry. Keep SDK typing uncertainty at the transport
  boundary; do not spread `Any` or blanket ignores into node code.
- Keep blocking file and media work off the host event loop. Bound queues,
  threads, memory, session duration, and cleanup time. Own, cancel, and await
  every created task; propagate cancellation after cleanup.
- Use verified model command schemas and track names. Discovery lists models;
  it does not prove that a model has a working node adapter.
- Validate refreshed discovery records separately and replace them atomically.
  Refresh must not execute provider text, install code, or open paid sessions.
- Own connection, upload, commands, recording, and teardown. Never retry session
  creation or a state-changing command after an ambiguous response.
- A dropped connection or paused track does not prove billing stopped. Preserve
  uncertain cleanup in private state and report a clear recovery action.
- Exclude HappyOyster. Do not add its nodes, dependencies, routes, or workflows.
- Keep credentials out of widgets, saved workflows, logs, and public files.
  Use the private credential store or environment configuration.
- Do not buy credits, enable top-ups, change billing, or query the user's Reactor
  dashboard or balance. Keep manual run records private.
- Use Comfy Desktop for manual workflow checks. Preserve user graphs, media,
  unrelated node packs, and browser tabs. Other web work uses a separate Chrome
  session.
