#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL='https://github.com/mahmoud/boltons'
UPSTREAM_REVISION='673e010d0afabc2f530e8d1f67f0a47c37afa7f4'
SOURCE_DIR=/tmp/boltons-src

git init "$SOURCE_DIR" >/dev/null
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch --depth 1 origin "$UPSTREAM_REVISION" >/dev/null
git -C "$SOURCE_DIR" checkout --detach FETCH_HEAD >/dev/null
cp -a "$SOURCE_DIR/." /workspace/
rm -rf /workspace/.github
