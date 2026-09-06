# Shell rules

Use small Bash wrappers with `set -euo pipefail`, quoted paths, preserved
arguments, and propagated exit codes. Put substantive logic in Python.
Keep wrappers compatible with macOS Bash and Git Bash.

Do not embed secrets, enable tracing around credentials, change global Git
settings, or install dependencies from a hook. Checks are read-only; formatting
and generation use separate tasks. Use [plain language](PLAIN_LANGUAGE.md) in
comments and diagnostics.

