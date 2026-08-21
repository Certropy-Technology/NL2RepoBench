#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL='https://github.com/hhatto/autopep8'
UPSTREAM_TAG='v2.3.2'
SOURCE_DIR=/tmp/autopep8-src

git init "$SOURCE_DIR" >/dev/null
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch --depth 1 origin "refs/tags/$UPSTREAM_TAG" >/dev/null
git -C "$SOURCE_DIR" checkout --detach FETCH_HEAD >/dev/null
cp -a "$SOURCE_DIR/." /workspace/
rm -rf /workspace/.github
