#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL='https://github.com/python-humanize/humanize'
UPSTREAM_REVISION='ce4147b6c8f8a132f772be0929d58305eb22c5d9'
SOURCE_DIR=/tmp/humanize-src

git init "$SOURCE_DIR" >/dev/null
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch --depth 1 origin "$UPSTREAM_REVISION" >/dev/null
git -C "$SOURCE_DIR" checkout --detach FETCH_HEAD >/dev/null
cp -a "$SOURCE_DIR/." /workspace/
rm -rf /workspace/.github
