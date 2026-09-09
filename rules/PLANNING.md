# Creating Plans

Create a plan when the user asks for one or the work needs a sequence of dependent
changes. Keep its detail proportional to the task. A small edit can use a short
list; a larger change needs enough detail to explain its scope and order.

## Plan content

State the intended result, the affected files or components, and the steps needed
to complete the work. Explain decisions that affect behavior or stored data.
Include concrete constraints and unresolved questions that affect implementation.

Do not require complete patches, full file contents, deletion diffs, or exact
asset-generation commands in every plan. Include them when the user asks for an
implementation-ready patch or when an exact example is needed to explain a change.
Do not invent abstractions, compatibility layers, or unrelated cleanup to fill out
an otherwise simple plan.

## Implementation order

Put dependent changes in order. Read the relevant implementation before choosing
an edit. Update affected callers and data with the new implementation, then remove
superseded code. Generate affected output after editing its source when generation
is part of the requested work.

Identify the affected workflow or media assets when a change includes them.
Describe the required result without reproducing every asset operation in advance.

## Verification scope

Do not create or run automated tests, or add test files or test commands to plans,
tasks, or hooks. Include formatting, linting, type checks, scans, builds, or manual
checks only when the user explicitly requests that verification.

Keep requested checks scoped to the affected behavior. For requested runtime
checks, use the installed package in Comfy Desktop. Distinguish source review,
static checks, and runtime results. Do not run checks in reference projects.

Keep plans and verification records private and out of public package files.
