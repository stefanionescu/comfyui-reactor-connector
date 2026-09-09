#!/usr/bin/env bash
# Runtime: Bash 3.2+, macOS and Linux.
#
# Run pip-audit against the locked Python environment.
set -euo pipefail

REPO_ROOT="${MISE_PROJECT_ROOT:-$(git rev-parse --show-toplevel)}"
cd "${REPO_ROOT}" || exit 1

# Audit locked dependencies without looking up the local connector on PyPI.
requirements_file="$(mktemp)"
trap 'rm -f "${requirements_file}"' EXIT
uv export --frozen --all-groups --no-emit-project \
  --no-header --no-annotate --output-file "${requirements_file}" >/dev/null
uv run --no-sync pip-audit \
  --strict \
  --require-hashes \
  --disable-pip \
  --requirement "${requirements_file}" \
  --progress-spinner off
