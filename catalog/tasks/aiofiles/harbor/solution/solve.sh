#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL='https://github.com/Tinche/aiofiles'
UPSTREAM_REVISION='1b3cfa9e6fbf59f7f0666ae809af7e9432c3a7c3'
SOURCE_DIR=/tmp/aiofiles-src

git init "$SOURCE_DIR" >/dev/null
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch --depth 1 origin "$UPSTREAM_REVISION" >/dev/null
git -C "$SOURCE_DIR" checkout --detach FETCH_HEAD >/dev/null
cp -a "$SOURCE_DIR/." /workspace/
rm -rf /workspace/.github
