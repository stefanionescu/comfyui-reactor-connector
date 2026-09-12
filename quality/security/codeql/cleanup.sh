#!/usr/bin/env bash
#
# Remove CodeQL databases below a verified repository root.
# Runtime: Bash 3.2+, macOS and Linux.
# Boundary: Owns recursive deletion for repository-managed CodeQL databases.

# codeql_remove_database - Remove one path below a verified repository root.
# Globals:
#   None.
# Arguments:
#   $1: Repository root.
#   $2: Path below the repository root.
# Outputs:
#   Writes validation failures to standard error.
# Returns:
#   0 when the path is absent or removed, non-zero when ownership is invalid.
codeql_remove_database() {
  local requested_root="$1"
  local target_path="$2"
  local owner_root

  [[ -n ${requested_root} && -n ${target_path} ]] || return 2
  owner_root="$(CDPATH='' cd -- "${requested_root}" && pwd -P)" || return 2
  [[ ${owner_root} != "/" && -f "${owner_root}/pyproject.toml" ]] || return 2
  case "${target_path}" in
    "${owner_root}" | "${owner_root}/" | *"/../"* | */..)
      return 2
      ;;
    "${owner_root}/"*) ;;
    *)
      return 2
      ;;
  esac
  if [[ -e ${target_path} || -L ${target_path} ]]; then
    rm -rf -- "${target_path}"
  fi
}
