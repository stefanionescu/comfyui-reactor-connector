#!/usr/bin/env bash
# Check the frontend CodeQL configuration before scanning.
set -euo pipefail

REPO_ROOT="${MISE_PROJECT_ROOT:-$(git rev-parse --show-toplevel)}"
cd "${REPO_ROOT}"

bun quality/security/codeql/frontend/integrity/paths.js
bun quality/security/codeql/frontend/integrity/false-positives.js
exec bash quality/security/codeql/frontend/scan.sh "$@"
