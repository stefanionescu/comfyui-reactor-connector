#!/usr/bin/env bash
# shellcheck shell=bash
# lint:justify -- reason: CodeQL scan policy is sourced by scanner scripts -- ticket: quality-security
# shellcheck disable=SC2034

CODEQL_LANGUAGE="python"
CODEQL_CONFIG_FILE="quality/config/security/codeql/python/scan.yml"
CODEQL_ARTIFACT_ROOT=".artifacts/security/codeql/python"
CODEQL_DATABASE_DIR="db-python"
CODEQL_SARIF_FILE="python.sarif"
CODEQL_SARIF_FORMAT="sarifv2.1.0"
CODEQL_QUERY_SUITES=(
  "codeql/python-queries@1.8.9:AlertSuppression.ql"
  "codeql/python-queries@1.8.9:codeql-suites/python-security-and-quality.qls"
  "codeql/python-queries@1.8.9:codeql-suites/python-security-extended.qls"
)
readonly CODEQL_LANGUAGE
readonly CODEQL_CONFIG_FILE
readonly CODEQL_ARTIFACT_ROOT
readonly CODEQL_DATABASE_DIR
readonly CODEQL_SARIF_FILE
readonly CODEQL_SARIF_FORMAT
readonly -a CODEQL_QUERY_SUITES
