#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL='https://github.com/benjaminp/six'
UPSTREAM_REVISION='c8e394065cd541a16c040515dc0afb85cf22a7c3'
SOURCE_DIR=/tmp/six-src

git init "$SOURCE_DIR" >/dev/null
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch --depth 1 origin "$UPSTREAM_REVISION" >/dev/null
git -C "$SOURCE_DIR" checkout --detach FETCH_HEAD >/dev/null
cp -a "$SOURCE_DIR/." /workspace/
rm -rf /workspace/.github
