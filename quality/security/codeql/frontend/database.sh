#!/usr/bin/env bash
# shellcheck disable=SC2154
# lint:justify -- reason: scan.sh supplies these values before sourcing and calling this file.
# Configure and run CodeQL database scans.

# configure_codeql_paths - Validates scan paths and prepares artifact paths.
configure_codeql_paths() {
  local source_root_abs="$1"
  local config_file_abs="$2"

  [[ -d ${source_root_abs} ]] || {
    printf 'error: source root not found: %s\n' "${source_root_abs}" >&2
    return 1
  }
  if [[ ! -f ${config_file_abs} ]]; then
    printf 'error: missing %s\n' "${config_file_abs}" >&2
    return 1
  fi

  artifact_root="${REPO_ROOT}/${CODEQL_ARTIFACT_ROOT}/${project_name}"
  database_dir="${artifact_root}/${CODEQL_DATABASE_DIR_PREFIX}${language}"
  sarif_file="${artifact_root}/${language}${CODEQL_SARIF_EXTENSION}"
  for artifact_parent in .artifacts .artifacts/security .artifacts/security/codeql .artifacts/security/codeql/frontend; do
    if [[ -L "${REPO_ROOT}/${artifact_parent}" ]]; then
      printf '%s\n' 'CodeQL artifact directories must not be symbolic links.' >&2
      return 1
    fi
  done
  mkdir -p -- "${artifact_root}" "$(dirname -- "${sarif_file}")"
}

# cleanup_codeql_database - Removes the database unless retention is enabled.
cleanup_codeql_database() {
  [[ ${keep_database} == '1' ]] && return 0
  [[ ${database_dir} == "${artifact_root}/${CODEQL_DATABASE_DIR_PREFIX}${language}" ]] || return 1
  rm -rf -- "${database_dir}"
}

# build_codeql_create_args - Builds database creation command arguments.
build_codeql_create_args() {
  local source_root_abs="$1"
  local config_file_abs="$2"

  create_args=(
    "${CODEQL_COMMAND}"
    database
    create
    "--language=${language}"
    "--source-root=${source_root_abs}"
    "--codescanning-config=${config_file_abs}"
    "--threads=${threads}"
    --overwrite
  )
  if [[ -n ${ram_mb} ]]; then
    create_args+=("--ram=${ram_mb}")
  fi
  create_args+=(--build-mode=none)
  create_args+=(-- "${database_dir}")
}

# build_codeql_analyze_args - Builds database analysis command arguments.
build_codeql_analyze_args() {
  analyze_args=(
    "${CODEQL_COMMAND}"
    database
    analyze
    "--format=${CODEQL_SARIF_FORMAT}"
    "--output=${sarif_file}"
    "--threads=${threads}"
    --no-print-diagnostics-summary
    --download
  )
  if [[ -n ${ram_mb} ]]; then
    analyze_args+=("--ram=${ram_mb}")
  fi
  analyze_args+=(-- "${database_dir}" "${query_suites[@]}")
}

# run_codeql_commands - Creates and analyzes the CodeQL database.
run_codeql_commands() {
  printf 'step=codeql project=%s language=%s status=running\n' \
    "${project_name}" "${language}" >&2
  "${create_args[@]}"
  "${analyze_args[@]}"
}
