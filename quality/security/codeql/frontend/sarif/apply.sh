#!/usr/bin/env bash
# Runtime: Bash 3.2+, macOS and Linux.
# shellcheck disable=SC2154
# lint:justify -- reason: scan.sh supplies these values before sourcing and calling this file.
# Apply CodeQL SARIF false-positive filters.

# filter_codeql_sarif - Removes configured false positives from SARIF output.
filter_codeql_sarif() {
  local config_file_abs="$1"
  local config_dir
  local false_positives_file
  config_dir="$(dirname -- "${config_file_abs}")"
  false_positives_file="${config_dir}/false-positives.json"

  if [[ ! -f ${false_positives_file} ]]; then
    printf '%s\n' 'Restore the required CodeQL finding policy before scanning.' >&2
    return 1
  fi
  bun "${FILTER_SARIF_SCRIPT}" "${sarif_file}" "${false_positives_file}"
}
