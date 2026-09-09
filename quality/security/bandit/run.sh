#!/usr/bin/env bash
# Runtime: Bash 3.2+, macOS and Linux.
#
# Run Bandit security checks.
set -euo pipefail

REPO_ROOT="${MISE_PROJECT_ROOT:-$(git rev-parse --show-toplevel)}"
cd "${REPO_ROOT}" || exit 1

uv run --no-sync bandit -c pyproject.toml -r __init__.py __main__.py src config scripts quality
