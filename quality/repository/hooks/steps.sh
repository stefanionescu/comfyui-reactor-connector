#!/usr/bin/env bash
set -euo pipefail

# run_step - Runs a hook step unless its skip variable is set.
run_step() {
  local name="$1"
  local skip_var="$2"
  local skip_value="0"
  shift 2

  if [[ -n ${skip_var} ]] && [[ -n ${!skip_var+x} ]]; then
    skip_value="${!skip_var}"
  fi
  if [[ -n ${skip_var} && ${skip_value} == "1" ]]; then
    printf '[hook] skipped %s (%s=1)\n' "${name}" "${skip_var}"
    return 0
  fi

  printf '[hook] %s\n' "${name}"
  "$@"
}
