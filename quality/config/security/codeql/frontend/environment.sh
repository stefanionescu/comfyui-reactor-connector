#!/usr/bin/env bash
# shellcheck shell=bash
# lint:justify -- reason: CodeQL policy is sourced by scanner scripts -- ticket: quality-config
# shellcheck disable=SC2034

CODEQL_COMMAND='codeql'
readonly CODEQL_COMMAND
CODEQL_ARTIFACT_ROOT='.artifacts/security/codeql'
readonly CODEQL_ARTIFACT_ROOT
CODEQL_DATABASE_DIR_PREFIX='db-'
readonly CODEQL_DATABASE_DIR_PREFIX
CODEQL_SARIF_EXTENSION='.sarif'
readonly CODEQL_SARIF_EXTENSION
CODEQL_SARIF_FORMAT='sarifv2.1.0'
readonly CODEQL_SARIF_FORMAT
CODEQL_DEFAULT_THREADS=0
readonly CODEQL_DEFAULT_THREADS
CODEQL_DEFAULT_KEEP_DB=0
readonly CODEQL_DEFAULT_KEEP_DB
CODEQL_JAVASCRIPT_QUERY_SUITES=(
  'codeql/javascript-queries@2.4.3:codeql-suites/javascript-security-and-quality.qls'
  'codeql/javascript-queries@2.4.3:codeql-suites/javascript-security-extended.qls'
)
readonly CODEQL_JAVASCRIPT_QUERY_SUITES

CODEQL_THREADS="${CODEQL_THREADS:-${CODEQL_DEFAULT_THREADS}}"
CODEQL_RAM_MB="${CODEQL_RAM_MB:-}"
CODEQL_KEEP_DB="${CODEQL_KEEP_DB:-${CODEQL_DEFAULT_KEEP_DB}}"
readonly CODEQL_THREADS CODEQL_RAM_MB CODEQL_KEEP_DB
