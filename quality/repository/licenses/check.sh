#!/usr/bin/env bash
#
# Run license-checker for one project.
set -euo pipefail

SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
readonly SCRIPT_DIR
REPO_ROOT="${MISE_PROJECT_ROOT:-$(git -C "${SCRIPT_DIR}" rev-parse --show-toplevel)}"
readonly REPO_ROOT
# shellcheck source=../../config/package-json/licenses/environment.sh
source "${REPO_ROOT}/quality/config/package-json/licenses/environment.sh"

CONFIG_FILE="${REPO_ROOT}/${LICENSE_CHECKER_CONFIG_FILE}"
readonly CONFIG_FILE
CONFIG_SCRIPT="${REPO_ROOT}/${LICENSE_CHECKER_POLICY_SCRIPT}"
readonly CONFIG_SCRIPT

cd "${REPO_ROOT}"

# main - Loads license policy and runs license-checker.
main() {
  local project="${1:-}"
  if [[ ${project} != frontend ]]; then
    printf '%s\n' "${LICENSE_CHECKER_USAGE}" >&2
    return 2
  fi
  if [[ ! -f ${CONFIG_FILE} ]]; then
    printf 'error: missing %s\n' "${CONFIG_FILE}" >&2
    return 1
  fi
  if [[ ! -f ${CONFIG_SCRIPT} ]]; then
    printf 'error: missing %s\n' "${CONFIG_SCRIPT}" >&2
    return 1
  fi

  local only_allow
  local exclude
  only_allow="$(bun "${CONFIG_SCRIPT}" "${CONFIG_FILE}" "${project}" "${LICENSE_CHECKER_ALLOW_MODE}")" ||
    return 1
  exclude="$(bun "${CONFIG_SCRIPT}" "${CONFIG_FILE}" "${project}" "${LICENSE_CHECKER_EXCLUDE_MODE}")" ||
    return 1

  declare -a command_args
  command_args=("${LICENSE_CHECKER_COMMAND[@]}" --onlyAllow "${only_allow}")
  [[ -z ${exclude} ]] || command_args+=(--excludePackages "${exclude}")
  "${command_args[@]}"
}

main "$@"
