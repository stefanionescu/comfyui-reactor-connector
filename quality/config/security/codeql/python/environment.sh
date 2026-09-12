#!/usr/bin/env bash
#
# Select the Python interpreter and language version for CodeQL analysis.
# Runtime: Bash 3.2+, macOS and Linux.
# shellcheck shell=bash
# lint:justify -- reason: CodeQL environment policy is sourced by scanner scripts
# shellcheck disable=SC2034
[[ -n ${_CFG_QLPY_READY:-} ]] && return 0
readonly _CFG_QLPY_READY=1

CODEQL_PYTHON_MAJOR_VERSION=3
CODEQL_PYTHON_ANALYSIS_VERSION="3.12"
CODEQL_PYTHON_EXECUTABLE_NAME="python3"
readonly CODEQL_PYTHON_MAJOR_VERSION
readonly CODEQL_PYTHON_ANALYSIS_VERSION
readonly CODEQL_PYTHON_EXECUTABLE_NAME
