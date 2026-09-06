# Working on Reactor for ComfyUI

Read the relevant rules before changing code:

- [General](rules/GENERAL.md), [Python](rules/PYTHON.md), and [naming](rules/NAMING.md).
- [ComfyUI](rules/COMFYUI.md), [Reactor](rules/REACTOR.md), and [frontend](rules/FRONTEND.md).
- [Documentation](rules/DOCUMENTATION.md), [plain language](rules/PLAIN_LANGUAGE.md),
  and [shell](rules/BASH.md).

All project text, including comments and generated help, must strictly conform
to ISO 24495 under the plain-language rule. Automated checks support review;
they cannot establish conformance alone.

Use the local PLAN.md when present; it is private planning material, excluded
from Git. Do not create or run tests. Do not recreate deleted test files.
Use formatting, linting, type checks, and asset builds for development.
Keep implementation status and run history out of public product text.

Use local mise tasks and Git hooks. Do not add Git-hosted workflows, Docker
rules, or inference deployment tooling. Use Bun for frontend dependencies and
commands, with bun.lock as the only frontend lockfile. Runtime code must not import
development tools. Keep credentials and private test evidence outside the repository.
