#!/usr/bin/env bash
#
# Create and analyze a Python CodeQL database.
set -euo pipefail

REPO_ROOT="${MISE_PROJECT_ROOT:-$(git rev-parse --show-toplevel)}"
readonly REPO_ROOT
cd "${REPO_ROOT}"

# shellcheck source=../../../config/security/codeql/python/environment.sh
source "${REPO_ROOT}/quality/config/security/codeql/python/environment.sh"
# shellcheck source=../../../config/security/codeql/python/scan.sh
source "${REPO_ROOT}/quality/config/security/codeql/python/scan.sh"

# _configure_codeql_python - Pins extraction to mise's project Python.
_configure_codeql_python() {
  local mise_python
  local mise_python_dir
  local resolved_python

  if ! mise_python="$(mise which "${CODEQL_PYTHON_EXECUTABLE_NAME}")"; then
    printf 'CodeQL requires the mise-managed project Python.\n' >&2
    return 1
  fi
  if [[ ! -x ${mise_python} ]]; then
    printf 'CodeQL Python is not executable: %s\n' "${mise_python}" >&2
    return 1
  fi

  mise_python_dir="${mise_python%/*}"
  PATH="${mise_python_dir}:${PATH}"
  export PATH
  if ! resolved_python="$(command -v "${CODEQL_PYTHON_EXECUTABLE_NAME}")"; then
    printf 'CodeQL could not resolve %s.\n' "${CODEQL_PYTHON_EXECUTABLE_NAME}" >&2
    return 1
  fi
  if [[ ${resolved_python} == "${REPO_ROOT}/.venv/"* ]]; then
    printf 'CodeQL refuses repository-venv interpreter: %s\n' "${resolved_python}" >&2
    return 1
  fi
  if [[ ${resolved_python%/*} != "${mise_python_dir}" ]]; then
    printf 'CodeQL resolved Python outside the mise installation: %s\n' "${resolved_python}" >&2
    return 1
  fi
}

# main - Creates and analyzes the repository Python CodeQL database.
main() {
  _configure_codeql_python

  export LGTM_PYTHON_SETUP_VERSION="${CODEQL_PYTHON_MAJOR_VERSION}"
  export CODEQL_EXTRACTOR_PYTHON_ANALYSIS_VERSION="${CODEQL_PYTHON_ANALYSIS_VERSION}"
  export CODEQL_EXTRACTOR_PYTHON_OPTION_PYTHON_EXECUTABLE_NAME="${CODEQL_PYTHON_EXECUTABLE_NAME}"

  mkdir -p "${CODEQL_ARTIFACT_ROOT}"
  codeql database create \
    --language="${CODEQL_LANGUAGE}" \
    --source-root="${REPO_ROOT}" \
    --codescanning-config="${CODEQL_CONFIG_FILE}" \
    --build-mode=none \
    --overwrite \
    "${CODEQL_ARTIFACT_ROOT}/${CODEQL_DATABASE_DIR}"
  codeql database analyze \
    --format="${CODEQL_SARIF_FORMAT}" \
    --output="${CODEQL_ARTIFACT_ROOT}/${CODEQL_SARIF_FILE}" \
    --download \
    "${CODEQL_ARTIFACT_ROOT}/${CODEQL_DATABASE_DIR}" \
    "${CODEQL_QUERY_SUITES[@]}"
  uv run --no-sync python -m quality.security.codeql.python.sarif \
    "${CODEQL_ARTIFACT_ROOT}/${CODEQL_SARIF_FILE}"
}

main "$@"
