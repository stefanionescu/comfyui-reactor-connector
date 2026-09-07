#!/usr/bin/env bash
# shellcheck shell=bash
# lint:justify -- reason: CodeQL environment policy is sourced by scanner scripts -- ticket: quality-security
# shellcheck disable=SC2034

CODEQL_PYTHON_MAJOR_VERSION=3
CODEQL_PYTHON_ANALYSIS_VERSION="3.12"
CODEQL_PYTHON_EXECUTABLE_NAME="python3"
readonly CODEQL_PYTHON_MAJOR_VERSION
readonly CODEQL_PYTHON_ANALYSIS_VERSION
readonly CODEQL_PYTHON_EXECUTABLE_NAME
