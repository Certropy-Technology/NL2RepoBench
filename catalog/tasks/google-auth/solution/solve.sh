#!/usr/bin/env bash
# Trusted Oracle solution. Only the Oracle run receives the run-scoped
# --allow-agent-host override for the frozen upstream source host; the model
# Agent runs with no-network and cannot reach GitHub.
set -euo pipefail

UPSTREAM_URL='https://github.com/googleapis/google-cloud-python.git'
UPSTREAM_REVISION='b4d97179f151d5ff37e6c7dbbd190a84c7d936a9'
SOURCE_DIR=/tmp/google-cloud-python-src

rm -rf "$SOURCE_DIR"
git init "$SOURCE_DIR" >/dev/null
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch --depth 1 origin "$UPSTREAM_REVISION" >/dev/null
git -C "$SOURCE_DIR" checkout --detach FETCH_HEAD >/dev/null

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
git -C "$SOURCE_DIR" archive --format=tar HEAD packages/google-auth \
    | tar -x --strip-components=2 -C /workspace

# The evaluator supplies its own hidden adapter, so the reference solution ships
# only the library itself.
rm -rf /workspace/system_tests
