#!/usr/bin/env bash
# shellcheck shell=bash
# lint:justify -- reason: scanner scripts consume these lockfile paths.
# shellcheck disable=SC2034
OSV_PYTHON_LOCKFILE="uv.lock"
OSV_FRONTEND_LOCKFILE="bun.lock"
readonly OSV_PYTHON_LOCKFILE OSV_FRONTEND_LOCKFILE
