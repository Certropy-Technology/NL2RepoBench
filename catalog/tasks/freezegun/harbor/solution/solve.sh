#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL='https://github.com/spulec/freezegun'
UPSTREAM_REVISION='92d61b3f5c31942a1039713574487bdcfcdbbfff'
SOURCE_DIR=/tmp/freezegun-src

git init "$SOURCE_DIR" >/dev/null
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch --depth 1 origin "$UPSTREAM_REVISION" >/dev/null
git -C "$SOURCE_DIR" checkout --detach FETCH_HEAD >/dev/null
cp -a "$SOURCE_DIR/." /workspace/
rm -rf /workspace/.github
