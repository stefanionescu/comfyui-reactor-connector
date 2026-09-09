#!/usr/bin/env bash
# Runtime: Bash 3.2+, macOS and Linux.
# shellcheck shell=bash
# lint:justify -- reason: root package policy is sourced by license scripts -- ticket: quality-config
# shellcheck disable=SC2034

[[ -n ${_CFG_LICENSES_READY:-} ]] && return 0
readonly _CFG_LICENSES_READY=1

LICENSE_CHECKER_CONFIG_FILE='.license-checker.json'
readonly LICENSE_CHECKER_CONFIG_FILE
LICENSE_CHECKER_POLICY_SCRIPT='quality/repository/licenses/read-policy.js'
readonly LICENSE_CHECKER_POLICY_SCRIPT
LICENSE_CHECKER_USAGE='Usage: check.sh <frontend>'
readonly LICENSE_CHECKER_USAGE
LICENSE_CHECKER_PROJECTS=(frontend)
readonly LICENSE_CHECKER_PROJECTS
LICENSE_CHECKER_ALLOW_MODE='only-allow'
readonly LICENSE_CHECKER_ALLOW_MODE
LICENSE_CHECKER_EXCLUDE_MODE='exclude'
readonly LICENSE_CHECKER_EXCLUDE_MODE
LICENSE_CHECKER_COMMAND=(bun --bun node_modules/license-checker/bin/license-checker)
readonly LICENSE_CHECKER_COMMAND
