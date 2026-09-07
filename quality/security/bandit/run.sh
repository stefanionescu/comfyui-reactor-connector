#!/usr/bin/env bash
#
# Run Bandit security checks.
set -euo pipefail

REPO_ROOT="${MISE_PROJECT_ROOT:-$(git rev-parse --show-toplevel)}"
cd "${REPO_ROOT}"

uv run --no-sync bandit -c pyproject.toml -r __init__.py __main__.py src config scripts quality
