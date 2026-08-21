#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL='https://github.com/rholder/retrying'
UPSTREAM_REVISION='3a435e8ba85d85d7300a3609cb6f3ba8cb4bc170'
SOURCE_DIR=/tmp/retrying-src

git init "$SOURCE_DIR" >/dev/null
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch --depth 1 origin "$UPSTREAM_REVISION" >/dev/null
git -C "$SOURCE_DIR" checkout --detach FETCH_HEAD >/dev/null
cp -a "$SOURCE_DIR/." /workspace/
rm -rf /workspace/.github
