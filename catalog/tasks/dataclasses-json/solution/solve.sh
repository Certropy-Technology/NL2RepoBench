#!/usr/bin/env bash
set -euo pipefail
UPSTREAM_URL='https://github.com/lidatong/dataclasses-json.git'
UPSTREAM_REVISION='dc63902eeb5e1c5ce1ea4e078c50e0eb9bc1a541'
SOURCE_DIR=/tmp/dataclasses-json-src
git init "$SOURCE_DIR" >/dev/null
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch --depth 1 origin "$UPSTREAM_REVISION" >/dev/null
git -C "$SOURCE_DIR" checkout --detach FETCH_HEAD >/dev/null
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
cp -a "$SOURCE_DIR"/. /workspace/
rm -rf /workspace/.git /workspace/.github /workspace/tests
